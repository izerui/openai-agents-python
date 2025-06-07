# Tracing

The Agents SDK includes built-in tracing, collecting a comprehensive record of events during an agent run: LLM generations, tool calls, handoffs, guardrails, and even custom events that occur. Using the [Traces dashboard](https://platform.openai.com/traces), you can debug, visualize, and monitor your workflows during development and in production.

(Agents SDK包含内置的追踪功能，可以全面记录agent运行期间的事件：LLM生成、工具调用、交接、防护栏以及发生的自定义事件。通过[Traces仪表盘](https://platform.openai.com/traces)，您可以在开发和产品环境中调试、可视化和监控工作流。)

!!!note

    Tracing is enabled by default. There are two ways to disable tracing:

    1. You can globally disable tracing by setting the env var `OPENAI_AGENTS_DISABLE_TRACING=1`
    2. You can disable tracing for a single run by setting [`agents.run.RunConfig.tracing_disabled`][] to `True`

(!!!note
    追踪功能默认启用。有两种禁用方式：
    1. 可以通过设置环境变量`OPENAI_AGENTS_DISABLE_TRACING=1`全局禁用
    2. 可以通过设置[`agents.run.RunConfig.tracing_disabled`][]为`True`来禁用单次运行)

***For organizations operating under a Zero Data Retention (ZDR) policy using OpenAI's APIs, tracing is unavailable.***

(***对于使用OpenAI API并遵循零数据保留(ZDR)政策的组织，追踪功能不可用。***)

## Traces and spans

-   **Traces** represent a single end-to-end operation of a "workflow". They're composed of Spans. Traces have the following properties:
    -   `workflow_name`: This is the logical workflow or app. For example "Code generation" or "Customer service".
    -   `trace_id`: A unique ID for the trace. Automatically generated if you don't pass one. Must have the format `trace_<32_alphanumeric>`.
    -   `group_id`: Optional group ID, to link multiple traces from the same conversation. For example, you might use a chat thread ID.
    -   `disabled`: If True, the trace will not be recorded.
    -   `metadata`: Optional metadata for the trace.
-   **Spans** represent operations that have a start and end time. Spans have:
    -   `started_at` and `ended_at` timestamps.
    -   `trace_id`, to represent the trace they belong to
    -   `parent_id`, which points to the parent Span of this Span (if any)
    -   `span_data`, which is information about the Span. For example, `AgentSpanData` contains information about the Agent, `GenerationSpanData` contains information about the LLM generation, etc.

(## 追踪和跨度
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
    -   `span_data`包含Span的信息，如`AgentSpanData`包含Agent信息，`GenerationSpanData`包含LLM生成信息等)

## Default tracing

By default, the SDK traces the following:

-   The entire `Runner.{run, run_sync, run_streamed}()` is wrapped in a `trace()`.
-   Each time an agent runs, it is wrapped in `agent_span()`
-   LLM generations are wrapped in `generation_span()`
-   Function tool calls are each wrapped in `function_span()`
-   Guardrails are wrapped in `guardrail_span()`
-   Handoffs are wrapped in `handoff_span()`
-   Audio inputs (speech-to-text) are wrapped in a `transcription_span()`
-   Audio outputs (text-to-speech) are wrapped in a `speech_span()`
-   Related audio spans may be parented under a `speech_group_span()`

By default, the trace is named "Agent trace". You can set this name if you use `trace`, or you can can configure the name and other properties with the [`RunConfig`][agents.run.RunConfig].

In addition, you can set up [custom trace processors](#custom-tracing-processors) to push traces to other destinations (as a replacement, or secondary destination).

(## 默认追踪
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

此外，您可以设置[自定义追踪处理器](#custom-tracing-processors)将追踪推送到其他目的地(作为替代或辅助目的地)。)

## Higher level traces

Sometimes, you might want multiple calls to `run()` to be part of a single trace. You can do this by wrapping the entire code in a `trace()`.

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

1. Because the two calls to `Runner.run` are wrapped in a `with trace()`, the individual runs will be part of the overall trace rather than creating two traces.

(## 高级追踪
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

1. 因为两个`Runner.run`调用都被包裹在`with trace()`中，所以单独运行将成为整体追踪的一部分，而不是创建两个追踪。)

## Creating traces

You can use the [`trace()`][agents.tracing.trace] function to create a trace. Traces need to be started and finished. You have two options to do so:

1. **Recommended**: use the trace as a context manager, i.e. `with trace(...) as my_trace`. This will automatically start and end the trace at the right time.
2. You can also manually call [`trace.start()`][agents.tracing.Trace.start] and [`trace.finish()`][agents.tracing.Trace.finish].

The current trace is tracked via a Python [`contextvar`](https://docs.python.org/3/library/contextvars.html). This means that it works with concurrency automatically. If you manually start/end a trace, you'll need to pass `mark_as_current` and `reset_current` to `start()`/`finish()` to update the current trace.

(## 创建追踪
可以使用[`trace()`][agents.tracing.trace]函数创建追踪。追踪需要启动和结束，有两种方式：
1. **推荐**：将追踪作为上下文管理器使用，即`with trace(...) as my_trace`，会在正确时间自动启动和结束追踪
2. 也可以手动调用[`trace.start()`][agents.tracing.Trace.start]和[`trace.finish()`][agents.tracing.Trace.finish]

当前追踪通过Python的[`contextvar`](https://docs.python.org/3/library/contextvars.html)跟踪，这意味着它能自动处理并发。如果手动启动/结束追踪，需要向`start()`/`finish()`传递`mark_as_current`和`reset_current`来更新当前追踪。)

## Creating spans

You can use the various [`*_span()`][agents.tracing.create] methods to create a span. In general, you don't need to manually create spans. A [`custom_span()`][agents.tracing.custom_span] function is available for tracking custom span information.

Spans are automatically part of the current trace, and are nested under the nearest current span, which is tracked via a Python [`contextvar`](https://docs.python.org/3/library/contextvars.html).

(## 创建跨度
可以使用各种[`*_span()`][agents.tracing.create]方法创建跨度。通常不需要手动创建跨度。[`custom_span()`][agents.tracing.custom_span]函数可用于跟踪自定义跨度信息。

跨度自动成为当前追踪的一部分，并嵌套在最近的当前跨度下，通过Python的[`contextvar`](https://docs.python.org/3/library/contextvars.html)跟踪。)

## Sensitive data

Certain spans may capture potentially sensitive data.

The `generation_span()` stores the inputs/outputs of the LLM generation, and `function_span()` stores the inputs/outputs of function calls. These may contain sensitive data, so you can disable capturing that data via [`RunConfig.trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data].

Similarly, Audio spans include base64-encoded PCM data for input and output audio by default. You can disable capturing this audio data by configuring [`VoicePipelineConfig.trace_include_sensitive_audio_data`][agents.voice.pipeline_config.VoicePipelineConfig.trace_include_sensitive_audio_data].

(## 敏感数据
某些跨度可能捕获潜在的敏感数据。

`generation_span()`存储LLM生成的输入/输出，`function_span()`存储函数调用的输入/输出。这些可能包含敏感数据，因此可以通过[`RunConfig.trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data]禁用捕获这些数据。

类似地，音频跨度默认包含输入和输出音频的base64编码PCM数据。可以通过配置[`VoicePipelineConfig.trace_include_sensitive_audio_data`][agents.voice.pipeline_config.VoicePipelineConfig.trace_include_sensitive_audio_data]禁用捕获此音频数据。)

## Custom tracing processors

The high level architecture for tracing is:

-   At initialization, we create a global [`TraceProvider`][agents.tracing.setup.TraceProvider], which is responsible for creating traces.
-   We configure the `TraceProvider` with a [`BatchTraceProcessor`][agents.tracing.processors.BatchTraceProcessor] that sends traces/spans in batches to a [`BackendSpanExporter`][agents.tracing.processors.BackendSpanExporter], which exports the spans and traces to the OpenAI backend in batches.

To customize this default setup, to send traces to alternative or additional backends or modifying exporter behavior, you have two options:

1. [`add_trace_processor()`][agents.tracing.add_trace_processor] lets you add an **additional** trace processor that will receive traces and spans as they are ready. This lets you do your own processing in addition to sending traces to OpenAI's backend.
2. [`set_trace_processors()`][agents.tracing.set_trace_processors] lets you **replace** the default processors with your own trace processors. This means traces will not be sent to the OpenAI backend unless you include a `TracingProcessor` that does so.

(## 自定义追踪处理器
追踪的高级架构是：
-   初始化时创建全局的[`TraceProvider`][agents.tracing.setup.TraceProvider]，负责创建追踪
-   配置`TraceProvider`使用[`BatchTraceProcessor`][agents.tracing.processors.BatchTraceProcessor]，将追踪/跨度批量发送到[`BackendSpanExporter`][agents.tracing.processors.BackendSpanExporter]，后者将跨度和追踪批量导出到OpenAI后端

要自定义此默认设置，将追踪发送到替代或额外的后端或修改导出行为，有两种选择：
1. [`add_trace_processor()`][agents.tracing.add_trace_processor]允许添加**额外的**追踪处理器，在追踪和跨度准备就绪时接收它们，除了发送到OpenAI后端外还可以进行自己的处理
2. [`set_trace_processors()`][agents.tracing.set_trace_processors]允许**替换**默认处理器为自己的追踪处理器，这意味着除非包含执行此操作的`TracingProcessor`，否则追踪不会发送到OpenAI后端)

## External tracing processors list

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

(## 外部追踪处理器列表
-   [Weights & Biases](https://weave-docs.wandb.ai/guides/integrations/openai_agents)
-   [Arize-Phoenix](https://docs.arize.com/phoenix/tracing/integrations-tracing/openai-agents-sdk)
-   [Future AGI](https://docs.futureagi.com/future-agi/products/observability/auto-instrumentation/openai_agents)
-   [MLflow (自托管/开源)](https://mlflow.org/docs/latest/tracing/integrations/openai-agent)
-   [MLflow (Databricks托管)](https://docs.databricks.com/aws/en/mlflow/mlflow-tracing#-automatic-tracing)
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
-   [Okahu-Monocle](https
