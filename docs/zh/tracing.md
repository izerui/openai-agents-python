# 追踪

Agents SDK包含内置的追踪功能，可以全面记录agent运行期间的事件：LLM生成、工具调用、交接、防护栏以及发生的自定义事件。通过[Traces仪表盘](https://platform.openai.com/traces)，您可以在开发和产品环境中调试、可视化和监控工作流。


!!!注意

    追踪功能默认启用。有两种禁用方式：
    1. 可以通过设置环境变量`OPENAI_AGENTS_DISABLE_TRACING=1`全局禁用
    2. 可以通过设置[`agents.run.RunConfig.tracing_disabled`][]为`True`来禁用单次运行


***对于使用OpenAI API并遵循零数据保留(ZDR)政策的组织，追踪功能不可用。***

## 追踪和跨度

-   **Traces**表示"工作流"的端到端操作，由Spans组成。Trace具有以下属性：
    -   `workflow_name`: 逻辑工作流或应用名称，如"代码生成"或"客户服务"
    -   `trace_id`: 追踪的唯一ID，不提供时会自动生成，格式必须为`trace_<32位字母数字>`
    -   `group_id`: 可选组ID，用于关联同一会话的多个追踪，如聊天线程ID
    -   `disabled`: 如果为True，则不会记录该追踪
    -   `metadata`: 可选的追踪元数据
-   **Spans**表示有开始和结束时间的操作，具有：
    -   `started_at`和`ended_at`时间戳
    -   `trace_id`表示所属的追踪
    -   `parent_id`指向该Span的父Span(如果有)
    -   `span_data`包含Span的信息，如`AgentSpanData`包含Agent信息，`GenerationSpanData`包含LLM生成信息等

## 默认追踪

SDK默认追踪以下内容：
-   整个`Runner.{run, run_sync, run_streamed}()`被包裹在`trace()`中
-   每次agent运行时被包裹在`agent_span()`中
-   LLM生成被包裹在`generation_span()`中
-   函数工具调用被包裹在`function_span()`中
-   防护栏被包裹在`guardrail_span()`中
-   交接被包裹在`handoff_span()`中
-   音频输入(语音转文字)被包裹在`transcription_span()`中
-   音频输出(文字转语音)被包裹在`speech_span()`中
-   相关音频跨度可能被归入`speech_group_span()`下

默认追踪名为"Agent trace"。使用`trace`时可以设置此名称，或通过[`RunConfig`][agents.run.RunConfig]配置名称和其他属性。

此外，您可以设置[自定义追踪处理器](#custom-tracing-processors)将追踪推送到其他目的地(作为替代或辅助目的地)。

## 高级追踪

有时您可能希望将多个`run()`调用作为单个追踪的一部分。可以通过将整个代码包裹在`trace()`中实现。

```python
from agents import Agent, Runner, trace

async def main():
    agent = Agent(name="Joke generator", instructions="Tell funny jokes.")

    with trace("Joke workflow"): # (1)!
        first_result = await Runner.run(agent, "Tell me a joke")
        second_result = await Runner.run(agent, f"Rate this joke: {first_result.final_output}")
        print(f"Joke: {first_result.final_output}")
        print(f"Rating: {second_result.final_output}")
```

1. 因为两个`Runner.run`调用都被包裹在`with trace()`中，所以单独运行将成为整体追踪的一部分，而不是创建两个追踪。

## 创建追踪

可以使用[`trace()`][agents.tracing.trace]函数创建追踪。追踪需要启动和结束，有两种方式：

1. **推荐**：将追踪作为上下文管理器使用，即`with trace(...) as my_trace`，会在正确时间自动启动和结束追踪
2. 也可以手动调用[`trace.start()`][agents.tracing.Trace.start]和[`trace.finish()`][agents.tracing.Trace.finish]

当前追踪通过Python的[`contextvar`](https://docs.python.org/3/library/contextvars.html)跟踪，这意味着它能自动处理并发。如果手动启动/结束追踪，需要向`start()`/`finish()`传递`mark_as_current`和`reset_current`来更新当前追踪。

## 创建跨度

可以使用各种[`*_span()`][agents.tracing.create]方法创建跨度。通常不需要手动创建跨度。[`custom_span()`][agents.tracing.custom_span]函数可用于跟踪自定义跨度信息。

跨度自动成为当前追踪的一部分，并嵌套在最近的当前跨度下，通过Python的[`contextvar`](https://docs.python.org/3/library/contextvars.html)跟踪。

## 敏感数据

某些跨度可能捕获潜在的敏感数据。

`generation_span()`存储LLM生成的输入/输出，`function_span()`存储函数调用的输入/输出。这些可能包含敏感数据，因此可以通过[`RunConfig.trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data]禁用捕获这些数据。

类似地，音频跨度默认包含输入和输出音频的base64编码PCM数据。可以通过配置[`VoicePipelineConfig.trace_include_sensitive_audio_data`][agents.voice.pipeline_config.VoicePipelineConfig.trace_include_sensitive_audio_data]禁用捕获此音频数据。

## 自定义追踪处理器

追踪的高级架构是：

-   初始化时创建全局的[`TraceProvider`][agents.tracing.setup.TraceProvider]，负责创建追踪
-   配置`TraceProvider`使用[`BatchTraceProcessor`][agents.tracing.processors.BatchTraceProcessor]，将追踪/跨度批量发送到[`BackendSpanExporter`][agents.tracing.processors.BackendSpanExporter]，后者将跨度和追踪批量导出到OpenAI后端

要自定义此默认设置，将追踪发送到替代或额外的后端或修改导出行为，有两种选择：

1. [`add_trace_processor()`][agents.tracing.add_trace_processor]允许添加**额外的**追踪处理器，在追踪和跨度准备就绪时接收它们，除了发送到OpenAI后端外还可以进行自己的处理
2. [`set_trace_processors()`][agents.tracing.set_trace_processors]允许**替换**默认处理器为自己的追踪处理器，这意味着除非包含执行此操作的`TracingProcessor`，否则追踪不会发送到OpenAI后端)

## 外部追踪处理器列表

-   [Weights & Biases](https://weave-docs.wandb.ai/guides/integrations/openai_agents)
-   [Arize-Phoenix](https://docs.arize.com/phoenix/tracing/integrations-tracing/openai-agents-sdk)
-   [Future AGI](https://docs.futureagi.com/future-agi/products/observability/auto-instrumentation/openai_agents)
-   [MLflow (self-hosted/OSS](https://mlflow.org/docs/latest/tracing/integrations/openai-agent)
-   [MLflow (Databricks hosted](https://docs.databricks.com/aws/en/mlflow/mlflow-tracing#-automatic-tracing)
-   [Braintrust](https://braintrust.dev/docs/guides/traces/integrations#openai-agents-sdk)
-   [Pydantic Logfire](https://logfire.pydantic.dev/docs/integrations/llms/openai/#openai-agents)
-   [AgentOps](https://docs.agentops.ai/v1/integrations/agentssdk)
-   [Scorecard](https://docs.scorecard.io/docs/documentation/features/tracing#openai-agents-sdk-integration)
-   [Keywords AI](https://docs.keywordsai.co/integration/development-frameworks/openai-agent)
-   [LangSmith](https://docs.smith.langchain.com/observability/how_to_guides/trace_with_openai_agents_sdk)
-   [Maxim AI](https://www.getmaxim.ai/docs/observe/integrations/openai-agents-sdk)
-   [Comet Opik](https://www.comet.com/docs/opik/tracing/integrations/openai_agents)
-   [Langfuse](https://langfuse.com/docs/integrations/openaiagentssdk/openai-agents)
-   [Langtrace](https://docs.langtrace.ai/supported-integrations/llm-frameworks/openai-agents-sdk)
-   [Okahu-Monocle](https://github.com/monocle2ai/monocle)
-   [Galileo](https://v2docs.galileo.ai/integrations/openai-agent-integration#openai-agent-integration)
-   [Portkey AI](https://portkey.ai/docs/integrations/agents/openai-agents)