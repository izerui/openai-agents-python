import asyncio

from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace
from agents.extensions.visualization import draw_graph

from examples.models import get_agent_chat_model

"""
此示例展示了代理作为工具的模式。前线代理接收用户消息，然后选择调用哪些代理作为工具。
在这种情况下，它从一组翻译代理中进行选择。
"""

deepseek = get_agent_chat_model('deepseek-v3')

spanish_agent = Agent(
    name="spanish_agent",
    instructions="您将用户的消息翻译成西班牙语",
    handoff_description="英语到西班牙语的翻译器",
    model=deepseek,
)

french_agent = Agent(
    name="french_agent",
    instructions="您将用户的消息翻译成法语",
    handoff_description="英语到法语的翻译器",
    model=deepseek,
)

italian_agent = Agent(
    name="italian_agent",
    instructions="您将用户的消息翻译成意大利语",
    handoff_description="英语到意大利语的翻译器",
    model=deepseek,
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "您是一个翻译代理。您使用提供给您的工具进行翻译。"
        "如果被要求进行多重翻译，您按顺序调用相关工具。"
        "您从不自己翻译，总是使用提供的工具。"
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="将用户的消息翻译成西班牙语",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="将用户的消息翻译成法语",
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="将用户的消息翻译成意大利语",
        ),
    ],
    model=deepseek,
)

draw_graph(orchestrator_agent).view()

synthesizer_agent = Agent(
    name="synthesizer_agent",
    instructions="您检查翻译，必要时进行更正，并生成最终的合并响应。",
    model=deepseek,
)


async def main():
    msg = input("你好！你想翻译什么内容，以及翻译成哪些语言？")

    # 在单个追踪中运行整个编排流程
    with trace("编排器评估器"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)

        for item in orchestrator_result.new_items:
            if isinstance(item, MessageOutputItem):
                text = ItemHelpers.text_message_output(item)
                if text:
                    print(f"  - 翻译步骤: {text}")

        synthesizer_result = await Runner.run(
            synthesizer_agent, orchestrator_result.to_input_list()
        )

    print(f"\n\n最终回复:\n{synthesizer_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
