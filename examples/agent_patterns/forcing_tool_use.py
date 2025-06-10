from __future__ import annotations

import asyncio
import os
import sys
from typing import Any, Literal

from pydantic import BaseModel

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolsToFinalOutputFunction,
    ToolsToFinalOutputResult,
    function_tool,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from examples.models import get_agent_chat_model

"""
本示例展示了如何强制 agent 使用工具。它通过 `ModelSettings(tool_choice="required")` 强制 agent 必须使用某个工具。

你可以用三种方式运行它：
1. `default`：默认行为，即将工具输出发送给 LLM。在这种情况下，`tool_choice` 没有设置，否则会导致无限循环——LLM 会一直调用工具，工具运行后又把结果发给 LLM，如此反复。
2. `first_tool_result`：第一个工具结果会被用作最终输出。
3. `custom`：使用自定义的工具使用行为函数。该自定义函数接收所有工具结果，并选择第一个工具结果作为最终输出。

用法：
python examples/agent_patterns/forcing_tool_use.py -t default
python examples/agent_patterns/forcing_tool_use.py -t first_tool
python examples/agent_patterns/forcing_tool_use.py -t custom
"""

class Weather(BaseModel):
    city: str
    temperature_range: str
    conditions: str


@function_tool
def get_weather(city: str) -> Weather:
    print("[debug] get_weather called")
    return Weather(city=city, temperature_range="14-20C", conditions="Sunny with wind")


async def custom_tool_use_behavior(
    context: RunContextWrapper[Any], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    weather: Weather = results[0].output
    return ToolsToFinalOutputResult(
        is_final_output=True, final_output=f"{weather.city} 的天气是 {weather.conditions}。"
    )


async def main(tool_use_behavior: Literal["default", "first_tool", "custom"] = "default"):
    if tool_use_behavior == "default":
        behavior: Literal["run_llm_again", "stop_on_first_tool"] | ToolsToFinalOutputFunction = (
            "run_llm_again"
        )
    elif tool_use_behavior == "first_tool":
        behavior = "stop_on_first_tool"
    elif tool_use_behavior == "custom":
        behavior = custom_tool_use_behavior

    deepseek = get_agent_chat_model('deepseek-v3')

    agent = Agent(
        name="天气 agent",
        instructions="你是一个乐于助人的 agent。",
        tools=[get_weather],
        tool_use_behavior=behavior,
        model_settings=ModelSettings(
            tool_choice="required" if tool_use_behavior != "default" else None
        ),
        model=deepseek,
    )

    result = await Runner.run(agent, input="东京的天气怎么样？")
    print(result.final_output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tool-use-behavior",
        type=str,
        required=True,
        choices=["default", "first_tool", "custom"],
        help="工具使用行为。default 表示工具输出会被发送给模型。first_tool_result 表示第一个工具结果会被用作最终输出。custom 表示使用自定义的工具使用行为函数。",
    )
    args = parser.parse_args()
    asyncio.run(main(args.tool_use_behavior))
