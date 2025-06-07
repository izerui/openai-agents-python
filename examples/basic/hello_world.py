import asyncio
import os

from openai import OpenAI, AsyncOpenAI, NOT_GIVEN

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
    set_tracing_disabled,
)

from dotenv import load_dotenv

load_dotenv(dotenv_path='../deepseek.env', verbose=True)

BASE_URL = os.getenv("OPENAI_BASE_URL") or ""
API_KEY = os.getenv("OPENAI_API_KEY") or ""
MODEL_NAME = os.getenv("OPENAI_MODEL_NAME") or ""

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY, EXAMPLE_MODEL_NAME via env var or code."
    )

"""此示例使用自定义提供商来访问Runner.run（），并直接呼叫OpenAI为其他人。
步骤：1。创建一个自定义OpenAI客户端。 
2。创建使用自定义客户端的模型推销员。 
3。只有在我们想使用自定义LLM提供商时，请在访问Runner.run（）的呼叫中使用Model -Providider。
请注意，在此示例中，我们在假设您没有Platform.openai.com的API键的假设下禁用跟踪。
如果您确实有一个，则可以设置`openai_api_key` env var var var var或call set_tracing_export_api_key（）设置特定键。
"""
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
# set_default_openai_api("chat_completions")
set_tracing_disabled(disabled=True)


class CustomModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name or MODEL_NAME, openai_client=client)


CUSTOM_MODEL_PROVIDER = CustomModelProvider()


async def main():
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = await Runner.run(
        agent,
        "Tell me about recursion in programming, 用中文回答.",
        run_config=RunConfig(model_provider=CUSTOM_MODEL_PROVIDER),
    )
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())
