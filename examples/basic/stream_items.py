import asyncio
import random

from agents import Agent, ItemHelpers, Runner, function_tool
from openai.types.responses import ResponseTextDeltaEvent

from examples.basic.lifecycle_example import deepseekv3
from examples.models import get_agent_chat_model


@function_tool
def how_many_jokes() -> int:
    """返回要讲的笑话数量"""
    return 3


async def main() -> None:
    agent = Agent(
        name="笑话讲述者",
        instructions="首先调用 how_many_jokes 工具，然后讲这么多个笑话。",
        tools=[how_many_jokes],
        model=deepseekv3,
    )

    result = Runner.run_streamed(
        agent,
        input="嗨，给我讲几个笑话。",
    )
    print("=== 开始运行 ===")
    async for event in result.stream_events():
        # 忽略原始响应事件增量
        if event.type == "raw_response_event":
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
            continue
        elif event.type == "agent_updated_stream_event":
            print(f"Agent 已更新: {event.new_agent.name}")
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- 工具被调用")
            elif event.item.type == "tool_call_output_item":
                print(f"-- 工具输出: {event.item.output}")
            elif event.item.type == "message_output_item":
                # 如果需要，我们可以在这里输出完整的消息内容
                # print("最终输出:")
                # print(f"-- 消息输出:\n {ItemHelpers.text_message_output(event.item)}")
                pass
            else:
                pass  # 忽略其他事件类型

    print("\n=== 运行完成 ===")


if __name__ == "__main__":
    asyncio.run(main())

    # === 开始运行 ===
    # Agent 已更新: Joker
    # -- 工具被调用
    # -- 工具输出: 4
    # -- 消息输出:
    #  当然，以下是四个笑话：
    #
    # 1. **为什么骷髅不互相打架？**
    #    因为他们没有胆量！
    #
    # 2. **你怎么称呼假意大利面？**
    #    冒牌货！
    #
    # 3. **为什么稻草人会获奖？**
    #    因为他在田野里表现出色！
    #
    # 4. **为什么自行车会摔倒？**
    #    因为它太累了！
    # === 运行完成 ===
