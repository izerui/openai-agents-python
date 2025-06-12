from pydantic import BaseModel

from agents import Agent

from examples.models import get_agent_chat_model

# 生成一个搜索计划来支持金融分析。
# 对于给定的金融问题或公司，我们需要搜索：
# 最新新闻、官方文件、分析师评论和其他
# 相关背景信息。
PROMPT = (
    "你是一位金融研究规划师。给定一个金融分析请求，"
    "制定一系列网络搜索来收集所需的背景信息。目标是获取最新的"
    "新闻标题、财报电话会议或10-K文件摘要、分析师评论和行业背景信息。"
    "请提供5到15个搜索关键词。"
)


class FinancialSearchItem(BaseModel):
    reason: str
    """此搜索项的相关性理由。"""

    query: str
    """用于网络（或文件）搜索的关键词。"""


class FinancialSearchPlan(BaseModel):
    searches: list[FinancialSearchItem]
    """要执行的搜索列表。"""

gpt = get_agent_chat_model('gpt')

planner_agent = Agent(
    name="FinancialPlannerAgent",
    instructions=PROMPT,
    model=gpt,
    output_type=FinancialSearchPlan,
)
