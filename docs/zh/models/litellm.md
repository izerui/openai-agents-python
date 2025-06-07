# Using any model via LiteLLM
(通过LiteLLM使用任意模型)

!!! note
(!!! 注意)

    The LiteLLM integration is in beta. You may run into issues with some model providers, especially smaller ones. Please report any issues via [Github issues](https://github.com/openai/openai-agents-python/issues) and we'll fix quickly.
    (LiteLLM集成目前处于测试阶段。您可能会遇到一些模型提供商的问题，特别是较小的提供商。请通过[Github issues](https://github.com/openai/openai-agents-python/issues)报告任何问题，我们会尽快修复。)

[LiteLLM](https://docs.litellm.ai/docs/) is a library that allows you to use 100+ models via a single interface. We've added a LiteLLM integration to allow you to use any AI model in the Agents SDK.
([LiteLLM](https://docs.litellm.ai/docs/)是一个允许您通过单一接口使用100多个模型的库。我们添加了LiteLLM集成，使您可以在Agents SDK中使用任何AI模型。)

## Setup
(设置)

You'll need to ensure `litellm` is available. You can do this by installing the optional `litellm` dependency group:
(您需要确保`litellm`可用。您可以通过安装可选的`litellm`依赖组来实现：)

```bash
pip install "openai-agents[litellm]"
```

Once done, you can use [`LitellmModel`][agents.extensions.models.litellm_model.LitellmModel] in any agent.
(完成后，您可以在任何agent中使用[`LitellmModel`][agents.extensions.models.litellm_model.LitellmModel]。)

## Example
(示例)

This is a fully working example. When you run it, you'll be prompted for a model name and API key. For example, you could enter:
(这是一个完整的工作示例。运行时，系统会提示您输入模型名称和API密钥。例如，您可以输入：)

-   `openai/gpt-4.1` for the model, and your OpenAI API key
-   `anthropic/claude-3-5-sonnet-20240620` for the model, and your Anthropic API key
-   etc

For a full list of models supported in LiteLLM, see the [litellm providers docs](https://docs.litellm.ai/docs/providers).
(有关LiteLLM支持的完整模型列表，请参阅[litellm providers文档](https://docs.litellm.ai/docs/providers)。)

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
