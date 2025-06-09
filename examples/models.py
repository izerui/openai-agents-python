import os

from agents import OpenAIChatCompletionsModel
from agents import (
    set_default_openai_api,
    set_default_openai_client,
    set_tracing_disabled,
    ModelProvider,
    Model
)
from dotenv import load_dotenv
from openai import AsyncOpenAI

file_dir = os.path.dirname(os.path.abspath(__file__))

def set_global_model(name: str = "gpt"):
    """
    Sets a global model provider for all requests by default.
    """

    load_dotenv(dotenv_path=os.path.join(file_dir, f'{name}.env'), verbose=True)

    BASE_URL = os.getenv("EXAMPLE_BASE_URL") or ""
    API_KEY = os.getenv("EXAMPLE_API_KEY") or ""
    MODEL_NAME = os.getenv("EXAMPLE_MODEL_NAME") or ""

    if not BASE_URL or not API_KEY or not MODEL_NAME:
        raise ValueError(
            "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY, EXAMPLE_MODEL_NAME via env var or code."
        )

    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
    )
    set_default_openai_client(client=client, use_for_tracing=False)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(disabled=True)


class CustomModelProvider(ModelProvider):
    def __init__(self, model_name: str | None = None, openai_client: AsyncOpenAI | None = None):
        """
        Initializes the custom model provider with an optional model name.
        If no model name is provided, it uses the default model name from the environment.
        """
        self.model_name = model_name
        self.openai_client = openai_client
        super().__init__()

    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name or self.model_name, openai_client=self.openai_client)


def get_runner_model_provider(name: str = "gpt"):
    """
    Returns a custom model provider that can be used in an Runner.
    """
    load_dotenv(dotenv_path=os.path.join(file_dir, f'{name}.env'), verbose=True)

    BASE_URL = os.getenv("EXAMPLE_BASE_URL") or ""
    API_KEY = os.getenv("EXAMPLE_API_KEY") or ""
    MODEL_NAME = os.getenv("EXAMPLE_MODEL_NAME") or ""

    if not BASE_URL or not API_KEY or not MODEL_NAME:
        raise ValueError(
            "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY, EXAMPLE_MODEL_NAME via env var or code."
        )

    """This example uses a custom provider for a specific agent. Steps:
    1. Create a custom OpenAI client.
    2. Create a `Model` that uses the custom client.
    3. Set the `model` on the Agent.

    Note that in this example, we disable tracing under the assumption that you don't have an API key
    from platform.openai.com. If you do have one, you can either set the `OPENAI_API_KEY` env var
    or call set_tracing_export_api_key() to set a tracing specific key.
    """
    client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
    set_tracing_disabled(disabled=True)

    return CustomModelProvider(model_name=MODEL_NAME, openai_client=client)


def get_agent_chat_model(name: str = "gpt"):
    """
    Returns a custom model that can be used in an Agent.
    """

    load_dotenv(dotenv_path=os.path.join(file_dir, f'{name}.env'), verbose=True)

    BASE_URL = os.getenv("EXAMPLE_BASE_URL") or ""
    API_KEY = os.getenv("EXAMPLE_API_KEY") or ""
    MODEL_NAME = os.getenv("EXAMPLE_MODEL_NAME") or ""

    if not BASE_URL or not API_KEY or not MODEL_NAME:
        raise ValueError(
            "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY, EXAMPLE_MODEL_NAME via env var or code."
        )

    """This example uses a custom provider for a specific agent. Steps:
    1. Create a custom OpenAI client.
    2. Create a `Model` that uses the custom client.
    3. Set the `model` on the Agent.

    Note that in this example, we disable tracing under the assumption that you don't have an API key
    from platform.openai.com. If you do have one, you can either set the `OPENAI_API_KEY` env var
    or call set_tracing_export_api_key() to set a tracing specific key.
    """
    client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
    set_tracing_disabled(disabled=True)

    return OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)