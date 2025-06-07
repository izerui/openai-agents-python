# Running agents (运行代理)

You can run agents via the [`Runner`][agents.run.Runner] class. You have 3 options: (您可以通过[`Runner`][agents.run.Runner]类运行代理，有3种选择：)

1. [`Runner.run()`][agents.run.Runner.run], which runs async and returns a [`RunResult`][agents.result.RunResult]. (异步运行并返回[`RunResult`][agents.result.RunResult])
2. [`Runner.run_sync()`][agents.run.Runner.run_sync], which is a sync method and just runs `.run()` under the hood. (同步方法，底层调用.run())
3. [`Runner.run_streamed()`][agents.run.Runner.run_streamed], which runs async and returns a [`RunResultStreaming`][agents.result.RunResultStreaming]. It calls the LLM in streaming mode, and streams those events to you as they are received. (异步运行并返回[`RunResultStreaming`][agents.result.RunResultStreaming]，以流式模式调用LLM并实时传输事件)

```python
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are a helpful assistant")

    result = await Runner.run(agent, "Write a haiku about recursion in programming.")
    print(result.final_output)
    # Code within the code,
    # Functions calling themselves,
    # Infinite loop's dance.
```

Read more in the [results guide](results.md). (更多信息请参阅[结果指南](results.md))

## The agent loop (代理循环)

When you use the run method in `Runner`, you pass in a starting agent and input. The input can either be a string (which is considered a user message), or a list of input items, which are the items in the OpenAI Responses API. (当使用Runner中的run方法时，您需要传入初始代理和输入。输入可以是字符串(视为用户消息)，也可以是OpenAI Responses API中的输入项列表)

The runner then runs a loop: (运行器会执行以下循环：)

1. We call the LLM for the current agent, with the current input. (为当前代理调用LLM，传入当前输入)
2. The LLM produces its output. (LLM产生输出)
    1. If the LLM returns a `final_output`, the loop ends and we return the result. (如果LLM返回final_output，循环结束并返回结果)
    2. If the LLM does a handoff, we update the current agent and input, and re-run the loop. (如果LLM执行交接，我们更新当前代理和输入，并重新运行循环)
    3. If the LLM produces tool calls, we run those tool calls, append the results, and re-run the loop. (如果LLM产生工具调用，我们运行这些工具调用，追加结果并重新运行循环)
3. If we exceed the `max_turns` passed, we raise a [`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded] exception. (如果超过max_turns限制，抛出[`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded]异常)

!!! note

    The rule for whether the LLM output is considered as a "final output" is that it produces text output with the desired type, and there are no tool calls. (LLM输出被视为"final output"的规则是：它产生具有所需类型的文本输出，并且没有工具调用)

## Streaming (流式传输)

Streaming allows you to additionally receive streaming events as the LLM runs. Once the stream is done, the [`RunResultStreaming`][agents.result.RunResultStreaming] will contain the complete information about the run, including all the new outputs produces. You can call `.stream_events()` for the streaming events. Read more in the [streaming guide](streaming.md). (流式传输允许您在LLM运行时接收流式事件。流结束后，[`RunResultStreaming`][agents.result.RunResultStreaming]将包含运行的完整信息，包括所有新产生的输出。您可以调用.stream_events()获取流式事件。更多信息请参阅[流式指南](streaming.md))

## Run config (运行配置)

The `run_config` parameter lets you configure some global settings for the agent run: (run_config参数允许您为代理运行配置一些全局设置：)

-   [`model`][agents.run.RunConfig.model]: Allows setting a global LLM model to use, irrespective of what `model` each Agent has. (设置全局LLM模型，覆盖各代理的模型设置)
-   [`model_provider`][agents.run.RunConfig.model_provider]: A model provider for looking up model names, which defaults to OpenAI. (模型提供者，用于查找模型名称，默认为OpenAI)
-   [`model_settings`][agents.run.RunConfig.model_settings]: Overrides agent-specific settings. For example, you can set a global `temperature` or `top_p`. (覆盖代理特定设置，例如可以设置全局temperature或top_p)
-   [`input_guardrails`][agents.run.RunConfig.input_guardrails], [`output_guardrails`][agents.run.RunConfig.output_guardrails]: A list of input or output guardrails to include on all runs. (包含在所有运行中的输入或输出防护栏列表)
-   [`handoff_input_filter`][agents.run.RunConfig.handoff_input_filter]: A global input filter to apply to all handoffs, if the handoff doesn't already have one. The input filter allows you to edit the inputs that are sent to the new agent. See the documentation in [`Handoff.input_filter`][agents.handoffs.Handoff.input_filter] for more details. (应用于所有交接的全局输入过滤器，允许编辑发送给新代理的输入)
-   [`tracing_disabled`][agents.run.RunConfig.tracing_disabled]: Allows you to disable [tracing](tracing.md) for the entire run. (允许禁用整个运行的[追踪](tracing.md))
-   [`trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data]: Configures whether traces will include potentially sensitive data, such as LLM and tool call inputs/outputs. (配置追踪是否包含潜在敏感数据，如LLM和工具调用的输入/输出)
-   [`workflow_name`][agents.run.RunConfig.workflow_name], [`trace_id`][agents.run.RunConfig.trace_id], [`group_id`][agents.run.RunConfig.group_id]: Sets the tracing workflow name, trace ID and trace group ID for the run. We recommend at least setting `workflow_name`. The group ID is an optional field that lets you link traces across multiple runs. (设置追踪工作流名称、追踪ID和追踪组ID，组ID是可选的，用于跨多个运行链接追踪)
-   [`trace_metadata`][agents.run.RunConfig.trace_metadata]: Metadata to include on all traces. (包含在所有追踪中的元数据)

## Conversations/chat threads (对话/聊天线程)

Calling any of the run methods can result in one or more agents running (and hence one or more LLM calls), but it represents a single logical turn in a chat conversation. For example: (调用任何运行方法可能导致一个或多个代理运行(因此有一个或多个LLM调用)，但它代表聊天对话中的单个逻辑轮次)

1. User turn: user enter text (用户轮次：用户输入文本)
2. Runner run: first agent calls LLM, runs tools, does a handoff to a second agent, second agent runs more tools, and then produces an output. (运行器运行：第一个代理调用LLM，运行工具，交接给第二个代理，第二个代理运行更多工具，然后产生输出)

At the end of the agent run, you can choose what to show to the user. For example, you might show the user every new item generated by the agents, or just the final output. Either way, the user might then ask a followup question, in which case you can call the run method again. (代理运行结束时，您可以选择向用户显示什么内容。例如，您可以显示代理生成的每个新项，或仅显示最终输出。无论哪种方式，用户可能会提出后续问题，这时您可以再次调用运行方法)

You can use the base [`RunResultBase.to_input_list()`][agents.result.RunResultBase.to_input_list] method to get the inputs for the next turn. (您可以使用[`RunResultBase.to_input_list()`][agents.result.RunResultBase.to_input_list]方法获取下一轮次的输入)

```python
async def main():
    agent = Agent(name="Assistant", instructions="Reply very concisely.")

    with trace(workflow_name="Conversation", group_id=thread_id):
        # First turn
        result = await Runner.run(agent, "What city is the Golden Gate Bridge in?")
        print(result.final_output)
        # San Francisco

        # Second turn
        new_input = result.to_input_list() + [{"role": "user", "content": "What state is it in?"}]
        result = await Runner.run(agent, new_input)
        print(result.final_output)
        # California
```

## Exceptions (异常)

The SDK raises exceptions in certain cases. The full list is in [`agents.exceptions`][]. As an overview: (SDK在某些情况下会抛出异常，完整列表见[`agents.exceptions`][]，概述如下：)

-   [`AgentsException`][agents.exceptions.AgentsException] is the base class for all exceptions raised in the SDK. (SDK中所有异常的基类)
-   [`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded] is raised when the run exceeds the `max_turns` passed to the run methods. (当运行超过max_turns限制时抛出)
-   [`ModelBehaviorError`][agents.exceptions.ModelBehaviorError] is raised when the model produces invalid outputs, e.g. malformed JSON or using non-existent tools. (当模型产生无效输出时抛出，如格式错误的JSON或使用不存在的工具)
-   [`UserError`][agents.exceptions.UserError] is raised when you (the person writing code using the SDK) make an error using the SDK. (当使用SDK时出错时抛出)
-   [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered], [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] is raised when a [guardrail](guardrails.md) is tripped. (当触发[防护栏](guardrails.md)时抛出)
