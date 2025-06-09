import asyncio
import random
from typing import Any

from pydantic import BaseModel

from agents import Agent, RunContextWrapper, RunHooks, Runner, Tool, Usage, function_tool, RunConfig, ModelSettings

from examples.models import get_agent_chat_model


class ExampleHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    def _usage_to_str(self, usage: Usage) -> str:
        return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"

    async def on_agent_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Agent {agent.name} started. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_agent_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Agent {agent.name} ended with output {output}. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Tool {tool.name} started. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Tool {tool.name} ended with result {result}. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_handoff(
        self, context: RunContextWrapper, from_agent: Agent, to_agent: Agent
    ) -> None:
        self.event_counter += 1
        print(
            f"### {self.event_counter}: Handoff from {from_agent.name} to {to_agent.name}. Usage: {self._usage_to_str(context.usage)}"
        )


hooks = ExampleHooks()

###


@function_tool
def random_number(max: int) -> int:
    """Generate a random number up to the provided max."""
    return random.randint(0, max)


@function_tool
def multiply_by_two(x: int) -> int:
    """Return x times two."""
    return x * 2


class FinalResult(BaseModel):
    number: int


deepseekv3 = get_agent_chat_model('deepseek-v3')

multiply_agent = Agent(
    name="乘法智能体",
    instructions=f"将数字乘以2，然后返回最终结果. 用json格式返回.json_schema: {FinalResult.model_json_schema()}",
    tools=[multiply_by_two],
    output_type=FinalResult,
    model=deepseekv3,
    model_settings=ModelSettings(temperature=0.1, extra_body={
        "response_format": {"type": "json_object"},
    }),
)

start_agent = Agent(
    name="随机数智能体",
    instructions=f"生成一个随机数。如果是，请停下来。如果很奇怪，请交给乘数代理. 用json格式返回. json_schema: {FinalResult.model_json_schema()}",
    tools=[random_number],
    output_type=FinalResult,
    handoffs=[multiply_agent],
    model=deepseekv3,
    model_settings=ModelSettings(temperature=0.1, extra_body={
        "response_format": {"type": "json_object"},
    }),
)


async def main() -> None:
    user_input = input("Enter a max number: ")
    result = await Runner.run(
        start_agent,
        hooks=hooks,
        input=f"在 0 和 {user_input} 之间生成一个随机数",
    )
    print(result.final_output)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
"""
$ python examples/basic/lifecycle_example.py

Enter a max number: 250
### 1: Agent Start Agent started. Usage: 0 requests, 0 input tokens, 0 output tokens, 0 total tokens
### 2: Tool random_number started. Usage: 1 requests, 148 input tokens, 15 output tokens, 163 total tokens
### 3: Tool random_number ended with result 101. Usage: 1 requests, 148 input tokens, 15 output tokens, 163 total tokens
### 4: Agent Start Agent started. Usage: 1 requests, 148 input tokens, 15 output tokens, 163 total tokens
### 5: Handoff from Start Agent to Multiply Agent. Usage: 2 requests, 323 input tokens, 30 output tokens, 353 total tokens
### 6: Agent Multiply Agent started. Usage: 2 requests, 323 input tokens, 30 output tokens, 353 total tokens
### 7: Tool multiply_by_two started. Usage: 3 requests, 504 input tokens, 46 output tokens, 550 total tokens
### 8: Tool multiply_by_two ended with result 202. Usage: 3 requests, 504 input tokens, 46 output tokens, 550 total tokens
### 9: Agent Multiply Agent started. Usage: 3 requests, 504 input tokens, 46 output tokens, 550 total tokens
### 10: Agent Multiply Agent ended with output number=202. Usage: 4 requests, 714 input tokens, 63 output tokens, 777 total tokens
Done!

"""
