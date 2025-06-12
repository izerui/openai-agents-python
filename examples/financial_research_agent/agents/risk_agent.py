from pydantic import BaseModel

from agents import Agent

from examples.models import get_agent_chat_model

# 专门负责识别风险因素和关注点的子代理
RISK_PROMPT = (
    "你是一位风险分析师，负责寻找公司前景中的潜在风险信号。"
    "根据背景研究，对风险进行简要分析，包括竞争威胁、"
    "监管问题、供应链问题或增长放缓等。分析内容请控制在2段以内。"
)


class AnalysisSummary(BaseModel):
    summary: str
    """此分析方面的简短文本摘要。"""

gpt = get_agent_chat_model('gpt')

risk_agent = Agent(
    name="RiskAnalystAgent",
    instructions=RISK_PROMPT,
    output_type=AnalysisSummary,
    model=gpt
)
