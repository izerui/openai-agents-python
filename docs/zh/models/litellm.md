# 通过LiteLLM使用任意模型

!!! 注意

    LiteLLM集成目前处于测试阶段。您可能会遇到一些模型提供商的问题，特别是较小的提供商。请通过[Github issues](https://github.com/openai/openai-agents-python/issues)报告任何问题，我们会尽快修复。

[LiteLLM](https://docs.litellm.ai/docs/) 是一个允许您通过单一接口使用100多个模型的库。我们添加了LiteLLM集成，使您可以在Agents SDK中使用任何AI模型。

## 安装

您需要确保`litellm`可用。您可以通过安装可选的`litellm`依赖组来实现：

```bash
pip install "openai-agents[litellm]"
```

完成后，您可以在任何agent中使用[`LitellmModel`][agents.extensions.models.litellm_model.LitellmModel]。

## 示例

这是一个完整的工作示例。运行时，系统会提示您输入模型名称和API密钥。例如，您可以输入：

-   `openai/gpt-4.1` for the model, and your OpenAI API key
-   `anthropic/claude-3-5-sonnet-20240620` for the model, and your Anthropic API key
-   etc

有关LiteLLM支持的完整模型列表，请参阅[litellm providers文档](https://docs.litellm.ai/docs/providers)。

```python
from __future__ import annotations

import asyncio

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main(model: str, api_key: str):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    # First try to get model/api key from args
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=False)
    parser.add_argument("--api-key", type=str, required=False)
    args = parser.parse_args()

    model = args.model
    if not model:
        model = input("Enter a model name for Litellm: ")

    api_key = args.api_key
    if not api_key:
        api_key = input("Enter an API key for Litellm: ")

    asyncio.run(main(model, api_key))
```