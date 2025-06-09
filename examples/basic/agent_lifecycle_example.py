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


gpt = get_agent_chat_model("gpt")

multiply_agent = Agent(
    name="乘代理",
    instructions="将数字乘以2，然后返回最终结果。",
    tools=[multiply_by_two],
    output_type=FinalResult,
    hooks=CustomAgentHooks(display_name="Multiply Agent"),
    model=gpt,
)

start_agent = Agent(
    name="开始代理",
    instructions="生成一个随机数。如果是偶数，请停下来。如果是奇数，请将其移交给乘代理。",
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
    hooks=CustomAgentHooks(display_name="Start Agent"),
    model=gpt,
)


async def main() -> None:
    user_input = input("Enter a max number: ")
    await Runner.run(
        start_agent,
        input=f"在0和{user_input}之间生成一个随机数。",
    )

    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
"""
$ python examples/basic/agent_lifecycle_example.py

Enter a max number: 250
### (Start Agent) 1: Agent Start Agent started
### (Start Agent) 2: Agent Start Agent started tool random_number
### (Start Agent) 3: Agent Start Agent ended tool random_number with result 37
### (Start Agent) 4: Agent Start Agent started
### (Start Agent) 5: Agent Start Agent handed off to Multiply Agent
### (Multiply Agent) 1: Agent Multiply Agent started
### (Multiply Agent) 2: Agent Multiply Agent started tool multiply_by_two
### (Multiply Agent) 3: Agent Multiply Agent ended tool multiply_by_two with result 74
### (Multiply Agent) 4: Agent Multiply Agent started
### (Multiply Agent) 5: Agent Multiply Agent ended with output number=74
Done!
"""
