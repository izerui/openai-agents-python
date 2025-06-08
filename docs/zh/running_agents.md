# 运行代理

您可以通过[`Runner`][agents.run.Runner]类运行代理，有3种选择：

1. 异步运行并返回[`RunResult`][agents.result.RunResult]
2. 同步方法，底层调用.run()
3. 异步运行并返回[`RunResultStreaming`][agents.result.RunResultStreaming]，以流式模式调用LLM并实时传输事件

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

更多信息请参阅[结果指南](results.md)

## 代理循环

当使用`Runner`中的`run`方法时，您需要传入初始代理和输入。输入可以是字符串(视为用户消息)，也可以是OpenAI Responses API中的输入项列表

运行器会执行以下循环：

1. 为当前代理调用LLM，传入当前输入
2. LLM产生输出
    1. 如果LLM返回`final_output`，循环结束并返回结果
    2. 如果LLM执行交接，我们更新当前代理和输入，并重新运行循环
    3. 如果LLM产生工具调用，我们运行这些工具调用，追加结果并重新运行循环
3. 如果超过`max_turns`限制，抛出[`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded]异常

!!! 说明

    LLM输出被视为"final output"的规则是：它产生具有所需类型的文本输出，并且没有工具调用

## 流式传输

流式传输允许您在LLM运行时接收流式事件。流结束后，[`RunResultStreaming`][agents.result.RunResultStreaming]将包含运行的完整信息，包括所有新产生的输出。您可以调用.stream_events()获取流式事件。更多信息请参阅[流式指南](streaming.md)

## 运行配置

run_config参数允许您为代理运行配置一些全局设置：

-   [`model`][agents.run.RunConfig.model]: 设置全局LLM模型，覆盖各代理的模型设置
-   [`model_provider`][agents.run.RunConfig.model_provider]: 模型提供者，用于查找模型名称，默认为OpenAI
-   [`model_settings`][agents.run.RunConfig.model_settings]: 覆盖代理特定设置，例如可以设置全局`temperature`或`top_p`
-   [`input_guardrails`][agents.run.RunConfig.input_guardrails], [`output_guardrails`][agents.run.RunConfig.output_guardrails]: 包含在所有运行中的输入或输出防护栏列表
-   [`handoff_input_filter`][agents.run.RunConfig.handoff_input_filter]: 应用于所有交接的全局输入过滤器，允许编辑发送给新代理的输入
-   [`tracing_disabled`][agents.run.RunConfig.tracing_disabled]: 允许禁用整个运行的[追踪](tracing.md)
-   [`trace_include_sensitive_data`][agents.run.RunConfig.trace_include_sensitive_data]: 配置追踪是否包含潜在敏感数据，如LLM和工具调用的输入/输出
-   [`workflow_name`][agents.run.RunConfig.workflow_name], [`trace_id`][agents.run.RunConfig.trace_id], [`group_id`][agents.run.RunConfig.group_id]: 设置追踪工作流名称、追踪ID和追踪组ID，组ID是可选的，用于跨多个运行链接追踪
-   [`trace_metadata`][agents.run.RunConfig.trace_metadata]: 包含在所有追踪中的元数据

## 对话/聊天线程

调用任何运行方法可能导致一个或多个代理运行(因此有一个或多个LLM调用)，但它代表聊天对话中的单个逻辑轮次

1. 用户轮次：用户输入文本
2. 运行器运行：第一个代理调用LLM，运行工具，交接给第二个代理，第二个代理运行更多工具，然后产生输出

代理运行结束时，您可以选择向用户显示什么内容。例如，您可以显示代理生成的每个新项，或仅显示最终输出。无论哪种方式，用户可能会提出后续问题，这时您可以再次调用运行方法

您可以使用[`RunResultBase.to_input_list()`][agents.result.RunResultBase.to_input_list]方法获取下一轮次的输入

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

## 异常

SDK在某些情况下会抛出异常，完整列表见[`agents.exceptions`][]，概述如下：

-   [`AgentsException`][agents.exceptions.AgentsException] SDK中所有异常的基类
-   [`MaxTurnsExceeded`][agents.exceptions.MaxTurnsExceeded] 当运行超过`max_turns`限制时抛出
-   [`ModelBehaviorError`][agents.exceptions.ModelBehaviorError] 当模型产生无效输出时抛出，如格式错误的JSON或使用不存在的工具
-   [`UserError`][agents.exceptions.UserError] 当使用SDK时出错时抛出
-   [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered], [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] 当触发[防护栏](guardrails.md)时抛出
