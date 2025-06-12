from pydantic import BaseModel

from agents import Agent

from examples.models import get_agent_chat_model

# 专注于分析公司基本面的子代理
FINANCIALS_PROMPT = (
    "你是一位专注于公司基本面的财务分析师，主要分析收入、利润、利润率和增长趋势等指标。"
    "给定一系列关于公司的网络搜索结果（以及可选的文件搜索结果），"
    "请简明扼要地分析其近期财务表现。提取关键指标或引用重要数据。"
    "分析内容请控制在2段以内。"
    "用中文回答，并确保分析内容清晰、简洁且易于理解。"
)


class AnalysisSummary(BaseModel):
    summary: str
    """此分析方面的简短文本摘要。"""


gpt = get_agent_chat_model('gpt')

financials_agent = Agent(
    name="FundamentalsAnalystAgent",
    instructions=FINANCIALS_PROMPT,
    output_type=AnalysisSummary,
    model=gpt
)
