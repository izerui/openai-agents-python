import asyncio
import random
from typing import Any

from pydantic import BaseModel

from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool

from examples.models import get_agent_chat_model


class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"### ({self.display_name}) {self.event_counter}: 代理 {agent.name} 已启动")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: 代理 {agent.name} 已完成，输出 {output}"
        )

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: 代理 {source.name} 移交给 {agent.name}"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: 代理 {agent.name} 开始调用工具 {tool.name}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: 代理 {agent.name} 完成工具 {tool.name} 调用，结果为 {result}"
        )


@function_tool
def random_number(max: int) -> int:
    """生成一个不超过指定最大值的随机数。"""
    return random.randint(0, max)


@function_tool
def multiply_by_two(x: int) -> int:
    """简单的乘以2运算。"""
    return x * 2


class FinalResult(BaseModel):
    number: int


gpt = get_agent_chat_model("gpt")

multiply_agent = Agent(
    name="乘法代理",
    instructions="将数字乘以2，然后返回最终结果。",
    tools=[multiply_by_two],
    output_type=FinalResult,
    hooks=CustomAgentHooks(display_name="乘法代理"),
    model=gpt,
)

start_agent = Agent(
    name="启动代理",
    instructions="生成一个随机数。如果是偶数，请停下来。如果是奇数，请将其移交给乘代理。",
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
    hooks=CustomAgentHooks(display_name="启动代理"),
    model=gpt,
)


async def main() -> None:
    user_input = input("请输入一个最大数字: ")
    await Runner.run(
        start_agent,
        input=f"在0和{user_input}之间生成一个随机数。",
    )

    print("完成！")


if __name__ == "__main__":
    asyncio.run(main())
"""
$ python examples/basic/agent_lifecycle_example.py

请输入一个最大数字: 250
### (启动代理) 1: 代理 启动代理 已启动
### (启动代理) 2: 代理 启动代理 开始调用工具 random_number
### (启动代理) 3: 代理 启动代理 完成工具 random_number 调用，结果为 37
### (启动代理) 4: 代理 启动代理 已启动
### (启动代理) 5: 代理 启动代理 移交给 乘法代理
### (乘法代理) 1: 代理 乘法代理 已启动
### (乘法代理) 2: 代理 乘法代理 开始调用工具 multiply_by_two
### (乘法代理) 3: 代理 乘法代理 完成工具 multiply_by_two 调用，结果为 74
### (乘法代理) 4: 代理 乘法代理 已启动
### (乘法代理) 5: 代理 乘法代理 已完成，输出数字=74
完成！
"""
