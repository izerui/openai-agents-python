from __future__ import annotations

import asyncio

from pydantic import BaseModel

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail, ModelSettings,
)

from examples.models import get_agent_chat_model

"""
本示例展示了如何使用防护栏(guardrails)。

防护栏是在 agent 执行过程中并行运行的检查机制。
它们可以用于以下场景：
- 检查输入消息是否偏离主题
- 检查输入消息是否违反任何政策
- 当检测到意外输入时接管 agent 的执行

在本例中，我们将设置一个输入防护栏，当用户要求完成数学作业时触发。
如果防护栏触发，我们将回复一个拒绝消息。
"""

deepseek = get_agent_chat_model('deepseek-v3')

### 1. 一个基于 agent 的防护栏，当用户要求完成数学作业时触发
class MathHomeworkOutput(BaseModel):
    reasoning: str
    is_math_homework: bool


guardrail_agent = Agent(
    name="防护栏检查",
    instructions=f"检查用户是否在要求你完成他们的数学作业。返回json数据，json_schema：{MathHomeworkOutput.model_json_schema()}",
    output_type=MathHomeworkOutput,
    model=deepseek,
    model_settings=ModelSettings(extra_body={
        "response_format": {"type": "json_object"},
    }),

)


@input_guardrail
async def math_guardrail(
    context: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """这是一个输入防护栏函数，它调用一个 agent 来检查输入是否是数学作业问题。
    """
    result = await Runner.run(guardrail_agent, input, context=context.context)
    final_output = result.final_output_as(MathHomeworkOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.is_math_homework,
    )


### 2. 运行循环


async def main():
    agent = Agent(
        name="客服代理",
        instructions="你是一个客服代理。你帮助客户解答他们的问题。",
        input_guardrails=[math_guardrail],
        model=deepseek,
    )

    input_data: list[TResponseInputItem] = []

    while True:
        user_input = input("输入消息: ")
        input_data.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = await Runner.run(agent, input_data)
            print(result.final_output)
            # 如果防护栏没有触发，我们将结果作为下一次运行的输入
            input_data = result.to_input_list()
        except InputGuardrailTripwireTriggered:
            # 如果防护栏触发，我们将拒绝消息添加到输入中
            message = "抱歉，我无法帮助你完成你的数学作业。"
            print(message)
            input_data.append(
                {
                    "role": "assistant",
                    "content": message,
                }
            )

    # 示例运行：
    # 输入消息: 加利福尼亚州的首府是哪里？
    # 加利福尼亚州的首府是萨克拉门托。
    # 输入消息: 你能帮我解这个方程吗：2x + 5 = 11
    # 抱歉，我无法帮助你完成你的数学作业。


if __name__ == "__main__":
    asyncio.run(main())
