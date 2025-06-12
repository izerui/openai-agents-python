from pydantic import BaseModel

from agents import Agent

from examples.models import get_agent_chat_model

# 用于检查综合报告的一致性和完整性的代理。
# 这可以用来标记潜在的遗漏或明显的错误。
VERIFIER_PROMPT = (
    "你是一位细心的审计员。你将审阅一份金融分析报告。"
    "你的工作是验证报告的内部一致性，确保引用来源清晰，且"
    "不包含无依据的论断。请指出任何问题或不确定之处。"
)


class VerificationResult(BaseModel):
    verified: bool
    """报告是否看起来连贯且合理。"""

    issues: str
    """如果未验证通过，描述主要问题或疑虑。"""

gpt = get_agent_chat_model('gpt')

verifier_agent = Agent(
    name="VerificationAgent",
    instructions=VERIFIER_PROMPT,
    model=gpt,
    output_type=VerificationResult,
)
