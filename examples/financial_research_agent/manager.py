from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence

from rich.console import Console

from agents import Runner, RunResult, custom_span, gen_trace_id, trace

from examples.financial_research_agent.agents.financials_agent import financials_agent
from examples.financial_research_agent.agents.planner_agent import (
    FinancialSearchItem,
    FinancialSearchPlan,
    planner_agent,
)
from examples.financial_research_agent.agents.risk_agent import risk_agent
from examples.financial_research_agent.agents.search_agent import search_agent
from examples.financial_research_agent.agents.verifier_agent import (
    VerificationResult,
    verifier_agent,
)
from examples.financial_research_agent.agents.writer_agent import (
    FinancialReportData,
    writer_agent,
)
from examples.financial_research_agent.printer import Printer


async def _summary_extractor(run_result: RunResult) -> str:
    """用于提取返回 AnalysisSummary 的子代理的自定义输出提取器。"""
    # 财务/风险分析师代理会输出一个带有 `summary` 字段的 AnalysisSummary
    # 我们希望工具调用只返回摘要文本，这样写作者可以直接内联使用它
    return str(run_result.final_output.summary)


class FinancialResearchManager:
    """
    协调整个流程：规划、搜索、子分析、写作和验证。
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    # 主入口方法：执行完整的金融研究流程
    # 包括：规划搜索、执行搜索、生成报告和验证
    async def run(self, query: str) -> None:
        trace_id = gen_trace_id()
        with trace("金融研究追踪", trace_id=trace_id):
            self.printer.update_item(
                "trace_id",
                f"查看追踪：https://platform.openai.com/traces/trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item("start", "正在启动金融研究...", is_done=True)
            search_plan = await self._plan_searches(query)
            search_results = await self._perform_searches(search_plan)
            report = await self._write_report(query, search_results)
            verification = await self._verify_report(report)

            final_report = f"报告摘要\n\n{report.short_summary}"
            self.printer.update_item("final_report", final_report, is_done=True)

            self.printer.end()

        # 输出到标准输出
        print("\n\n=====报告=====\n\n")
        print(f"报告内容：\n{report.markdown_report}")
        print("\n\n=====后续问题=====\n\n")
        print("\n".join(report.follow_up_questions))
        print("\n\n=====验证结果=====\n\n")
        print(verification)

    # 规划搜索阶段：根据用户查询生成搜索计划
    # 返回：包含多个搜索项的搜索计划
    async def _plan_searches(self, query: str) -> FinancialSearchPlan:
        self.printer.update_item("planning", "正在规划搜索...")
        result = await Runner.run(planner_agent, f"查询：{query}")
        self.printer.update_item(
            "planning",
            f"将执行 {len(result.final_output.searches)} 次搜索",
            is_done=True,
        )
        return result.final_output_as(FinancialSearchPlan)

    # 执行搜索阶段：并行执行所有计划的搜索
    # 返回：搜索结果列表
    async def _perform_searches(self, search_plan: FinancialSearchPlan) -> Sequence[str]:
        with custom_span("搜索网络"):
            self.printer.update_item("searching", "搜索中...")
            tasks = [asyncio.create_task(self._search(item)) for item in search_plan.searches]
            results: list[str] = []
            num_completed = 0
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
                self.printer.update_item(
                    "searching", f"搜索中... {num_completed}/{len(tasks)} 已完成"
                )
            self.printer.mark_item_done("searching")
            return results

    # 执行单个搜索：处理单个搜索项
    # 返回：搜索结果或 None（如果搜索失败）
    async def _search(self, item: FinancialSearchItem) -> str | None:
        input_data = f"搜索词：{item.query}\n原因：{item.reason}"
        try:
            result = await Runner.run(search_agent, input_data)
            return str(result.final_output)
        except Exception:
            return None

    # 撰写报告阶段：整合搜索结果并生成分析报告
    # 包括：基本面分析、风险分析和完整报告生成
    async def _write_report(self, query: str, search_results: Sequence[str]) -> FinancialReportData:
        # 将专业分析师作为工具暴露出来，以便写作者可以内联调用它们
        # 并仍然生成最终的 FinancialReportData 输出
        fundamentals_tool = financials_agent.as_tool(
            tool_name="fundamentals_analysis",
            tool_description="获取关键财务指标的简要分析",
            custom_output_extractor=_summary_extractor,
        )
        risk_tool = risk_agent.as_tool(
            tool_name="risk_analysis",
            tool_description="获取潜在风险因素的简要分析",
            custom_output_extractor=_summary_extractor,
        )
        writer_with_tools = writer_agent.clone(tools=[fundamentals_tool, risk_tool])
        self.printer.update_item("writing", "正在思考报告结构...")
        input_data = f"原始查询：{query}\n搜索结果摘要：{search_results}"
        result = Runner.run_streamed(writer_with_tools, input_data)
        update_messages = [
            "正在规划报告结构...",
            "正在撰写各个部分...",
            "正在完成报告...",
        ]
        last_update = time.time()
        next_message = 0
        async for _ in result.stream_events():
            if time.time() - last_update > 5 and next_message < len(update_messages):
                self.printer.update_item("writing", update_messages[next_message])
                next_message += 1
                last_update = time.time()
        self.printer.mark_item_done("writing")
        return result.final_output_as(FinancialReportData)

    # 验证报告阶段：检查报告的完整性和一致性
    # 返回：验证结果，包含是否通过验证及问题说明
    async def _verify_report(self, report: FinancialReportData) -> VerificationResult:
        self.printer.update_item("verifying", "正在验证报告...")
        result = await Runner.run(verifier_agent, report.markdown_report)
        self.printer.mark_item_done("verifying")
        return result.final_output_as(VerificationResult)
