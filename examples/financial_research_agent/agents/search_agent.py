from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings

from examples.models import get_agent_chat_model

# 根据搜索词使用网络搜索获取简要摘要。
# 摘要应该简明扼要但要包含主要的财务要点。
INSTRUCTIONS = (
    "你是一位专门研究金融主题的研究助理。"
    "根据给定的搜索词，使用网络搜索获取最新的相关信息，"
    "并生成一个不超过300字的简短摘要。重点关注对金融分析师有用的"
    "关键数据、事件或引用。"
)

gpt = get_agent_chat_model('gpt')

search_agent = Agent(
    name="FinancialSearchAgent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
    model=gpt,
    model_settings=ModelSettings(tool_choice="required"),
)
