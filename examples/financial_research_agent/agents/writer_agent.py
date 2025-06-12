from pydantic import BaseModel

from agents import Agent

from examples.models import get_agent_chat_model

# 写作代理负责整合原始搜索结果，并可选择调用
# 专业分析子代理以获取专业评论，最终生成一份完整的 markdown 报告。
WRITER_PROMPT = (
    "你是一位资深金融分析师。你将获得原始查询和一组原始搜索摘要。"
    "你的任务是将这些内容整合成一份长篇 markdown 报告（至少包含几个段落），"
    "需要包含一个简短的执行摘要和后续问题。如有需要，你可以调用可用的分析工具"
    "（如 fundamentals_analysis、risk_analysis）来获取专业分析师的简短评论并整合进去。"
)


class FinancialReportData(BaseModel):
    short_summary: str
    """2-3句话的执行摘要。"""

    markdown_report: str
    """完整的 markdown 格式报告。"""

    follow_up_questions: list[str]
    """建议的后续研究问题。"""

gpt = get_agent_chat_model('gpt')

# 注意：我们将在管理器运行时附加专业分析师代理的调用。
# 这展示了一个代理如何使用调用来委托专业子代理。
writer_agent = Agent(
    name="FinancialWriterAgent",
    instructions=WRITER_PROMPT,
    model=gpt,
    output_type=FinancialReportData,
)
