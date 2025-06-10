import asyncio
import json
from dataclasses import dataclass
from typing import Any

from agents import Agent, AgentOutputSchema, AgentOutputSchemaBase, Runner

from examples.models import set_global_model

"""本示例演示了如何使用非严格模式的输出类型。严格模式
允许我们确保输出有效的 JSON，但有些模式并不兼容严格模式。

在本示例中，我们定义了一个不兼容严格模式的输出类型，然后
使用 strict_json_schema=False 运行 agent。

我们还展示了一个自定义输出类型。

要了解哪些模式兼容严格模式，请参见：
https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#supported-schemas
"""

set_global_model('gpt')

@dataclass
class OutputType:
    """
    一个简单的、不兼容严格模式的输出类型。
    @param jokes: 笑话列表，以笑话编号为索引。
    """
    jokes: dict[int, str]


class OutputSchema(AgentOutputSchemaBase):
    """用于告诉 LLM 如何格式化其输出的模式。

    我们不必总是定义这个，但对于复杂的输出类型来说这样做很有帮助。它只是让我们能
    在 prompt 中提供一些格式化指令。
    """

    @classmethod
    def get_json_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "jokes": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
        }

    @classmethod
    def get_example_data(cls) -> dict[str, Any]:
        """提供一个如何格式化输出的例子"""
        return {
            "jokes": {
                1: "为什么章鱼喜欢听笑话？因为它有八个笑点！",
                2: "为什么鱼从不穿鞋？因为它们已经有了鳍！",
            },
        }


async def main():
    agent = Agent(
        name="笑话生成器",
        instructions="生成 3 个有趣的笑话。保持简短和友好。",
        output_type=OutputType,
        output_schema=OutputSchema,
        # 因为我们使用的是不兼容严格模式的模式，所以需要关闭严格模式
        strict_json_schema=False,
    )

    result = await Runner.run(agent, "给我讲几个笑话。")
    output = result.final_output_as(OutputType)
    print(json.dumps(output.jokes, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
