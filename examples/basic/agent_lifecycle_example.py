import asyncio
import random
from typing import Any

from pydantic import BaseModel

from agents import Agent, AgentHooks, RunContextWrapper, Runner, Tool, function_tool
from examples.basic.lifecycle_example import max_number


class CustomAgentHooks(AgentHooks):
    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} started")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended with output {output}"
        )

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {source.name} handed off to {agent.name}"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} started tool {tool.name}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### ({self.display_name}) {self.event_counter}: Agent {agent.name} ended tool {tool.name} with result {result}"
        )


###


@function_tool
def random_number(max: int) -> int:
    """
    Generate a random number up to the provided maximum.
    """
    return random.randint(0, max)


@function_tool
def multiply_by_two(x: int) -> int:
    """Simple multiplication by two."""
    return x * 2


class FinalResult(BaseModel):
    number: int


multiply_agent = Agent(
    name="Multiply Agent",
    instructions="Multiply the number by 2 and then return the final result.",
    tools=[multiply_by_two],
    output_type=FinalResult,
    hooks=CustomAgentHooks(display_name="Multiply Agent"),
)

start_agent = Agent(
    name="Start Agent",
    instructions="Generate a random number. If it's even, stop. If it's odd, hand off to the multiply agent.",
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
    hooks=CustomAgentHooks(display_name="Start Agent"),
)

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
    user_input = input("Enter a max number: ")
    try:
        max_number = int(user_input)
        await Runner.run(
            start_agent,
            input=f"Generate a random number between 0 and {max_number}.",
        )
        print("Done!")
    except ValueError:
        print("请输入有效的整数")
        return

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