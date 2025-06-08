# 结果

当你调用`Runner.run`方法时，你会得到以下两种结果之一：

-   如果调用`run`或`run_sync`会得到[`RunResult`][agents.result.RunResult]
-   如果调用`run_streamed`会得到[`RunResultStreaming`][agents.result.RunResultStreaming]

两者都继承自[`RunResultBase`][agents.result.RunResultBase]，其中包含了最有用的信息

## 最终输出

[`final_output`][agents.result.RunResultBase.final_output]属性包含最后运行的agent的最终输出，可能是以下两种情况之一：

-   如果最后一个agent没有定义`output_type`，则是一个`str`字符串
-   如果agent定义了输出类型，则是一个`last_agent.output_type`类型的对象

!!! 说明

    `final_output` 的类型是 `Any`。我们无法对其进行静态类型定义，这是因为存在交接情况。如果发生交接，意味着任何 Agent 都可能是最后一个 agent，所以我们无法静态地知道所有可能的输出类型。


## 下一轮的输入

你可以使用[`result.to_input_list()`][agents.result.RunResultBase.to_input_list]将结果转换为输入列表，该列表将你提供的原始输入与agent运行期间生成的项连接起来。这样可以方便地将一个agent运行的输出传递给另一个运行，或者在循环中运行并每次追加新的用户输入

## 最后一个agent

[`last_agent`][agents.result.RunResultBase.last_agent]属性包含最后运行的agent。根据你的应用场景，这在用户下次输入时通常很有用。例如，如果你有一个前端分诊agent将任务转交给特定语言的agent，你可以存储最后一个agent，并在用户下次发送消息时重新使用它

## 新生成的项

[`new_items`][agents.result.RunResultBase.new_items]属性包含运行期间生成的新项。这些项是[`RunItem`][agents.items.RunItem]类型。运行项包装了LLM生成的原始项

-   [`MessageOutputItem`][agents.items.MessageOutputItem]表示来自LLM的消息。原始项是生成的消息
-   [`HandoffCallItem`][agents.items.HandoffCallItem]表示LLM调用了handoff工具。原始项是来自LLM的工具调用项
-   [`HandoffOutputItem`][agents.items.HandoffOutputItem]表示发生了handoff。原始项是对handoff工具调用的工具响应。你还可以从该项访问源/目标agent
-   [`ToolCallItem`][agents.items.ToolCallItem]表示LLM调用了一个工具
-   [`ToolCallOutputItem`][agents.items.ToolCallOutputItem]表示调用了工具。原始项是工具响应。你还可以从该项访问工具输出
-   [`ReasoningItem`][agents.items.ReasoningItem]表示来自LLM的推理项。原始项是生成的推理内容

## 其他信息

### 防护栏结果

[`input_guardrail_results`][agents.result.RunResultBase.input_guardrail_results]和[`output_guardrail_results`][agents.result.RunResultBase.output_guardrail_results]属性包含防护栏的结果(如果有的话)。防护栏结果有时可能包含你想要记录或存储的有用信息，所以我们把这些信息提供给你

### 原始响应

[`raw_responses`][agents.result.RunResultBase.raw_responses]属性包含LLM生成的[`ModelResponse`][agents.items.ModelResponse]

### 原始输入

[`input`][agents.result.RunResultBase.input]属性包含你提供给`run`方法的原始输入。在大多数情况下你不需要这个，但在你需要时它是可用的
