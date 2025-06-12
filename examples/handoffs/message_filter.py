from __future__ import annotations

import json
import random

from agents import Agent, HandoffInputData, Runner, function_tool, handoff, trace
from agents.extensions import handoff_filters


@function_tool
def random_number_tool(max: int) -> int:
    """返回一个介于 0 和给定最大值之间的随机整数。"""
    return random.randint(0, max)


def spanish_handoff_message_filter(handoff_message_data: HandoffInputData) -> HandoffInputData:
    # 首先，我们将从消息历史记录中删除所有与工具相关的消息
    handoff_message_data = handoff_filters.remove_all_tools(handoff_message_data)

    # 其次，我们还将删除历史记录中的前两项，仅用于演示
    history = (
        tuple(handoff_message_data.input_history[2:])
        if isinstance(handoff_message_data.input_history, tuple)
        else handoff_message_data.input_history
    )

    return HandoffInputData(
        input_history=history,
        pre_handoff_items=tuple(handoff_message_data.pre_handoff_items),
        new_items=tuple(handoff_message_data.new_items),
    )


first_agent = Agent(
    name="助手",
    instructions="请保持回答非常简洁。",
    tools=[random_number_tool],
)

spanish_agent = Agent(
    name="西班牙语助手",
    instructions="你只说西班牙语，并且回答非常简洁。",
    handoff_description="一个说西班牙语的助手。",
)

second_agent = Agent(
    name="助手",
    instructions=(
        "做一个有帮助的助手。如果用户说西班牙语，请转交给西班牙语助手。"
    ),
    handoffs=[handoff(spanish_agent, input_filter=spanish_handoff_message_filter)],
)


async def main():
    # 将整个运行过程作为单个工作流进行追踪
    with trace(workflow_name="消息过滤"):
        # 1. 向第一个代理发送普通消息
        result = await Runner.run(first_agent, input="你好，我叫 Sora。")

        print("步骤 1 完成")

        # 2. 让它生成一个随机数
        result = await Runner.run(
            first_agent,
            input=result.to_input_list()
            + [{"content": "你能生成一个介于 0 和 100 之间的随机数吗？", "role": "user"}],
        )

        print("步骤 2 完成")

        # 3. 调用第二个代理
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "我住在纽约市。这个城市的人口是多少？",
                    "role": "user",
                }
            ],
        )

        print("步骤 3 完成")

        # 4. 触发语言切换移交
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "Por favor habla en español. ¿Cuál es mi nombre y dónde vivo?",
                    "role": "user",
                }
            ],
        )

        print("步骤 4 完成")

    print("\n===最终消息列表===\n")

    # 5. 这将触发 spanish_handoff_message_filter 的调用
    # 输出将不包含前两条消息，且没有工具调用
    # 让我们打印消息看看结果如何
    for message in result.to_input_list():
        print(json.dumps(message, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
