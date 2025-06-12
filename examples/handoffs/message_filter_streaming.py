from __future__ import annotations

import json
import random

from agents import Agent, HandoffInputData, Runner, function_tool, handoff, trace, AgentHooks, RunContextWrapper, \
    TContext
from agents.extensions import handoff_filters

from examples.agent_patterns.input_guardrails import deepseek
from examples.basic.agent_lifecycle_example import CustomAgentHooks
from examples.models import get_agent_chat_model


@function_tool
def random_number_tool(max: int) -> int:
    """生成一个0到指定最大值之间的随机整数。"""
    return random.randint(0, max)


def spanish_handoff_message_filter(handoff_message_data: HandoffInputData) -> HandoffInputData:
    # 首先，从消息历史中删除所有与工具相关的消息
    handoff_message_data = handoff_filters.remove_all_tools(handoff_message_data)

    # 其次，为了演示，我们也会删除历史记录中的前两项
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


deepseek = get_agent_chat_model('deepseek-v3')

# 第一个代理：简洁助手
first_agent = Agent(
    name="简洁助手",
    instructions="保持极度简洁的回答。",
    tools=[random_number_tool],
    model=deepseek,
)

class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.display_name = display_name

    async def on_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext]) -> None:
        print(f'当{self.display_name} 代理处理的请求已开始。')
        return await super().on_start(context, agent)


# 西班牙语代理
spanish_agent = Agent(
    name="西班牙语助手",
    instructions="只使用西班牙语交流，并保持极度简洁。",
    handoff_description="一个西班牙语助手。",
    model=deepseek,
    hooks=CustomAgentHooks(display_name="西班牙语助手")
)


def on_spanish_agent_handoff(_ctx: RunContextWrapper[None], data = None) -> None:
    print('开始交接到西班牙语助手。')

# 第二个代理：通用助手
second_agent = Agent(
    name="通用助手",
    instructions=(
        "作为一个有帮助的助手。如果用户使用西班牙语，则转交给西班牙语助手。"
    ),
    handoffs=[handoff(spanish_agent, input_filter=spanish_handoff_message_filter, on_handoff=on_spanish_agent_handoff)],
    model=deepseek,
)


async def main():
    # 将整个运行过程追踪为单个工作流
    with trace(workflow_name="消息过滤流式处理示例"):
        # 1. 向第一个代理发送普通消息
        result = await Runner.run(first_agent, input="你好，我叫小明。")

        print("第1步完成")

        # 2. 请求生成一个随机数
        result = await Runner.run(
            first_agent,
            input=result.to_input_list()
            + [{"content": "能给我生成一个0到100之间的随机数吗？", "role": "user"}],
        )

        print("第2步完成")

        # 3. 调用第二个代理
        result = await Runner.run(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "我住在北京。北京的人口是多少？",
                    "role": "user",
                }
            ],
        )

        print("第3步完成")

        # 4. 触发向西班牙语助手的转交
        stream_result = Runner.run_streamed(
            second_agent,
            input=result.to_input_list()
            + [
                {
                    "content": "Por favor habla en español. ¿Cuál es mi nombre y dónde vivo?",
                    "role": "user",
                }
            ],
        )
        async for _ in stream_result.stream_events():
            pass

        print("第4步完成")

    print("\n===最终消息===\n")

    # 5. 这应该导致调用spanish_handoff_message_filter，因此输出应该缺少前两条消息，并且没有工具调用。
    # 让我们打印消息以查看发生了什么
    for item in stream_result.to_input_list():
        print(json.dumps(item, indent=2))
        """
        $python examples/handoffs/message_filter_streaming.py
        第1步完成
        第2步完成
        第3步完成
        Tu nombre y lugar de residencia no los tengo disponibles. Solo sé que mencionaste vivir en Beijing.
        第4步完成

        ===最终消息===

        {
            "content": "能给我生成一个0到100之间的随机数吗？",
            "role": "user"
        }
        {
            "id": "...",
            "content": [
                {
                "annotations": [],
                "text": "好的！这是一个0到100之间的随机数：**37**。",
                "type": "output_text"
                }
            ],
            "role": "assistant",
            "status": "completed",
            "type": "message"
        }
        {
            "content": "我住在北京。北京的人口是多少？",
            "role": "user"
        }
        {
            "id": "...",
            "content": [
                {
                "annotations": [],
                "text": "根据最新估计，北京的人口约为2100万人。您想了解更多关于北京的信息吗？",
                "type": "output_text"
                }
            ],
            "role": "assistant",
            "status": "completed",
            "type": "message"
        }
        {
            "content": "Por favor habla en español. ¿Cuál es mi nombre y dónde vivo?",
            "role": "user"
        }
        {
            "id": "...",
            "content": [
                {
                "annotations": [],
                "text": "No sé tu nombre, pero me dijiste que vives en Beijing.",
                "type": "output_text"
                }
            ],
            "role": "assistant",
            "status": "completed",
            "type": "message"
        }
        """

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
