from __future__ import annotations

import asyncio
import json

from pydantic import BaseModel, Field

from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)

from examples.models import get_agent_chat_model

"""
本示例展示了如何使用输出防护栏。

输出防护栏是对 agent 最终输出进行检查的机制。
它们可以用于以下场景：
- 检查输出是否包含敏感数据
- 检查输出是否是对用户消息的有效响应

在本例中，我们将使用一个（设定的）示例，检查 agent 的响应中是否包含电话号码。
"""


# agent 的输出类型
class MessageOutput(BaseModel):
    reasoning: str = Field(description="关于如何回应用户消息的思考过程")
    response: str = Field(description="对用户消息的回应")
    user_name: str | None = Field(description="发送消息的用户名称（如果已知）")


@output_guardrail
async def sensitive_data_check(
    context: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    """检查输出中是否包含敏感数据（在本例中是电话号码）。
    """
    phone_number_in_response = "650" in output.response
    phone_number_in_reasoning = "650" in output.reasoning

    return GuardrailFunctionOutput(
        output_info={
            "phone_number_in_response": phone_number_in_response,
            "phone_number_in_reasoning": phone_number_in_reasoning,
        },
        tripwire_triggered=phone_number_in_response or phone_number_in_reasoning,
    )

gpt = get_agent_chat_model('gpt')

agent = Agent(
    name="助手",
    instructions="你是一个乐于助人的助手。",
    output_type=MessageOutput,
    output_guardrails=[sensitive_data_check],
    model=gpt,
)


async def main():
    # 这应该没问题
    await Runner.run(agent, "加利福尼亚州的首府是哪里？")
    print("第一条消息通过")

    # 这应该会触发防护栏
    try:
        result = await Runner.run(
            agent, "我的电话号码是 650-123-4567。你觉得我住在哪里？"
        )
        print(
            f"防护栏没有触发 - 这是意外的。输出: {json.dumps(result.final_output.model_dump(), indent=2)}"
        )

    except OutputGuardrailTripwireTriggered as e:
        print(f"防护栏触发。信息: {e.guardrail_result.output.output_info}")


if __name__ == "__main__":
    asyncio.run(main())
