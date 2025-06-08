# 模型

Agents SDK内置支持两种OpenAI模型：

-   推荐使用[`OpenAIResponsesModel`][agents.models.openai_responses.OpenAIResponsesModel]，它使用新的[Responses API](https://platform.openai.com/docs/api-reference/responses)调用OpenAI接口
-   [`OpenAIChatCompletionsModel`][agents.models.openai_chatcompletions.OpenAIChatCompletionsModel]使用[Chat Completions API](https://platform.openai.com/docs/api-reference/chat)调用OpenAI接口

## 非OpenAI模型

您可以通过[LiteLLM集成](./litellm.md)使用大多数其他非OpenAI模型。首先安装litellm依赖组：

```bash
pip install "openai-agents[litellm]"
```

然后使用`litellm/`前缀调用任何[支持的模型](https://docs.litellm.ai/docs/providers)：

```python
claude_agent = Agent(model="litellm/anthropic/claude-3-5-sonnet-20240620", ...)
gemini_agent = Agent(model="litellm/gemini/gemini-2.5-flash-preview-04-17", ...)
```

### 使用非OpenAI模型的其他方式

您还可以通过以下3种方式集成其他LLM提供商(示例[在此](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers/))：

1. [`set_default_openai_client`][agents.set_default_openai_client]适用于您想全局使用`AsyncOpenAI`实例作为LLM客户端的情况。这适用于LLM提供商具有OpenAI兼容API端点，并且您可以设置`base_url`和`api_key`的情况。参见[examples/model_providers/custom_example_global.py](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers/custom_example_global.py)中的可配置示例
2. [`ModelProvider`][agents.models.interface.ModelProvider]在`Runner.run`级别。这允许您指定"在此运行中为所有代理使用自定义模型提供商"。参见[examples/model_providers/custom_example_provider.py](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers/custom_example_provider.py)中的可配置示例
3. [`Agent.model`][agents.agent.Agent.model]允许您在特定Agent实例上指定模型。这使您可以为不同代理混合匹配不同的提供商。参见[examples/model_providers/custom_example_agent.py](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers/custom_example_agent.py)中的可配置示例。使用大多数可用模型的简单方法是通过[LiteLLM集成](./litellm.md)

如果您没有来自`platform.openai.com`的API密钥，我们建议通过`set_tracing_disabled()`禁用跟踪，或设置[不同的跟踪处理器](../tracing.md)

!!! 注意

    在这些示例中，我们使用Chat Completions API/模型，因为大多数LLM提供商尚不支持Responses API。如果您的LLM提供商支持它，我们建议使用Responses

## 混合匹配模型

在单个工作流中，您可能希望为每个代理使用不同的模型。例如，您可以使用更小、更快的模型进行分类，而使用更大、功能更强的模型处理复杂任务。配置[`Agent`][agents.Agent]时，您可以通过以下方式选择特定模型：

1. 传递模型名称
2. 传递任何模型名称+可以将该名称映射到Model实例的[`ModelProvider`][agents.models.interface.ModelProvider]
3. 直接提供[`Model`][agents.models.interface.Model]实现

!!!注意

    虽然我们的SDK同时支持[`OpenAIResponsesModel`][agents.models.openai_responses.OpenAIResponsesModel]和[`OpenAIChatCompletionsModel`][agents.models.openai_chatcompletions.OpenAIChatCompletionsModel]两种形式，但我们建议每个工作流使用单一模型形式，因为这两种形式支持不同的功能和工具集。如果您的工作流需要混合匹配模型形式，请确保您使用的所有功能在两者上都可用

```python
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
import asyncio

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
    model="o3-mini", # (1)!
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model=OpenAIChatCompletionsModel( # (2)!
        model="gpt-4o",
        openai_client=AsyncOpenAI()
    ),
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    model="gpt-3.5-turbo",
)

async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
```

1.  直接设置OpenAI模型名称
2.  提供[`Model`][agents.models.interface.Model]实现

当您想进一步配置代理使用的模型时，可以传递[`ModelSettings`][agents.models.interface.ModelSettings]，它提供可选的模型配置参数，如temperature

```python
from agents import Agent, ModelSettings

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
    model="gpt-4o",
    model_settings=ModelSettings(temperature=0.1),
)
```

## 使用其他LLM提供商的常见问题

### 跟踪客户端错误401

如果您收到与跟踪相关的错误，这是因为跟踪数据会上传到OpenAI服务器，而您没有OpenAI API密钥。您有三种解决方法：

1. 完全禁用跟踪：[`set_tracing_disabled(True)`][agents.set_tracing_disabled]
2. 为跟踪设置OpenAI密钥：[`set_tracing_export_api_key(...)`][agents.set_tracing_export_api_key]。此API密钥仅用于上传跟踪数据，且必须来自[platform.openai.com](https://platform.openai.com/)
3. 使用非OpenAI跟踪处理器。参见[跟踪文档](../tracing.md#custom-tracing-processors)

### Responses API支持

SDK默认使用Responses API，但大多数其他LLM提供商尚不支持它。您可能会看到404或类似问题。解决方法有两种：

1. 调用[`set_default_openai_api("chat_completions")`][agents.set_default_openai_api]。如果您通过环境变量设置`OPENAI_API_KEY`和`OPENAI_BASE_URL`，这将有效
2. 使用[`OpenAIChatCompletionsModel`][agents.models.openai_chatcompletions.OpenAIChatCompletionsModel]。示例[在此](https://github.com/openai/openai-agents-python/tree/main/examples/model_providers/)

### 结构化输出支持

一些模型提供商不支持[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)。这有时会导致如下错误：

```

BadRequestError: Error code: 400 - {'error': {'message': "'response_format.type' : value is not one of the allowed values ['text','json_object']", 'type': 'invalid_request_error'}}

```

这是某些模型提供商的缺点-它们支持JSON输出，但不允许您指定用于输出的`json_schema`。我们正在解决这个问题，但我们建议依赖确实支持JSON模式输出的提供商，否则您的应用程序经常会因为格式错误的JSON而中断

## 跨提供商混合模型

您需要了解模型提供商之间的功能差异，否则可能会遇到错误。例如，OpenAI支持结构化输出、多模态输入以及托管的文件搜索和网络搜索，但许多其他提供商不支持这些功能。请注意这些限制：

-   不要向不支持的提供商发送它们不理解的`tools`
-   在调用纯文本模型之前过滤掉多模态输入
-   请注意，不支持结构化JSON输出的提供商偶尔会产生无效的JSON
