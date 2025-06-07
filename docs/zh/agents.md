# Agents (智能体)

Agents are the core building block in your apps. An agent is a large language model (LLM), configured with instructions and tools.
(智能体是您应用程序中的核心构建块。一个智能体是一个配置了指令和工具的大语言模型(LLM)。)

## Basic configuration (基础配置)

The most common properties of an agent you'll configure are:
(您最常配置的智能体属性包括：)

-   `instructions`: also known as a developer message or system prompt.
   (`instructions`：也称为开发者消息或系统提示。)
-   `model`: which LLM to use, and optional `model_settings` to configure model tuning parameters like temperature, top_p, etc.
   (`model`：使用哪个LLM，以及可选的`model_settings`来配置模型调优参数如temperature、top_p等。)
-   `tools`: Tools that the agent can use to achieve its tasks.
   (`tools`：智能体可以用来完成任务的各种工具。)

```python
from agents import Agent, ModelSettings, function_tool

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny"

agent = Agent(
    name="Haiku agent",
    instructions="Always respond in haiku form",
    model="o3-mini",
    tools=[get_weather],
)
```

## Context (上下文)

Agents are generic on their `context` type. Context is a dependency-injection tool: it's an object you create and pass to `Runner.run()`, that is passed to every agent, tool, handoff etc, and it serves as a grab bag of dependencies and state for the agent run. You can provide any Python object as the context.
(智能体是泛型于其`context`类型的。上下文是一个依赖注入工具：它是您创建并传递给`Runner.run()`的对象，会被传递给每个智能体、工具、交接等，作为智能体运行时的依赖和状态的集合。您可以提供任何Python对象作为上下文。)

```python
@dataclass
class UserContext:
    uid: str
    is_pro_user: bool

    async def fetch_purchases() -> list[Purchase]:
        return ...

agent = Agent[UserContext](
    ...,
)
```

## Output types (输出类型)

By default, agents produce plain text (i.e. `str`) outputs. If you want the agent to produce a particular type of output, you can use the `output_type` parameter. A common choice is to use [Pydantic](https://docs.pydantic.dev/) objects, but we support any type that can be wrapped in a Pydantic [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/) - dataclasses, lists, TypedDict, etc.
(默认情况下，智能体产生纯文本(即`str`)输出。如果您希望智能体产生特定类型的输出，可以使用`output_type`参数。常见的选择是使用[Pydantic](https://docs.pydantic.dev/)对象，但我们支持任何可以被Pydantic [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/)包装的类型 - 数据类、列表、TypedDict等。)

```python
from pydantic import BaseModel
from agents import Agent


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

agent = Agent(
    name="Calendar extractor",
    instructions="Extract calendar events from text",
    output_type=CalendarEvent,
)
```

!!! note

    When you pass an `output_type`, that tells the model to use [structured outputs](https://platform.openai.com/docs/guides/structured-outputs) instead of regular plain text responses.
    (当您传递`output_type`时，这会告诉模型使用[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)而不是常规的纯文本响应。)

## Handoffs (交接)

Handoffs are sub-agents that the agent can delegate to. You provide a list of handoffs, and the agent can choose to delegate to them if relevant. This is a powerful pattern that allows orchestrating modular, specialized agents that excel at a single task. Read more in the [handoffs](handoffs.md) documentation.
(交接是智能体可以委托的子智能体。您提供交接列表，智能体可以在相关时选择委托给它们。这是一种强大的模式，允许编排模块化、专门化的智能体，每个智能体都擅长单一任务。更多信息请参阅[交接](handoffs.md)文档。)

```python
from agents import Agent

booking_agent = Agent(...)
refund_agent = Agent(...)

triage_agent = Agent(
    name="Triage agent",
    instructions=(
        "Help the user with their questions."
        "If they ask about booking, handoff to the booking agent."
        "If they ask about refunds, handoff to the refund agent."
    ),
    handoffs=[booking_agent, refund_agent],
)
```

## Dynamic instructions (动态指令)

In most cases, you can provide instructions when you create the agent. However, you can also provide dynamic instructions via a function. The function will receive the agent and context, and must return the prompt. Both regular and `async` functions are accepted.
(在大多数情况下，您可以在创建智能体时提供指令。但是，您也可以通过函数提供动态指令。该函数将接收智能体和上下文，并且必须返回提示。常规函数和`async`函数都被接受。)

```python
def dynamic_instructions(
    context: RunContextWrapper[UserContext], agent: Agent[UserContext]
) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."


agent = Agent[UserContext](
    name="Triage agent",
    instructions=dynamic_instructions,
)
```

## Lifecycle events (hooks) (生命周期事件/钩子)

Sometimes, you want to observe the lifecycle of an agent. For example, you may want to log events, or pre-fetch data when certain events occur. You can hook into the agent lifecycle with the `hooks` property. Subclass the [`AgentHooks`][agents.lifecycle.AgentHooks] class, and override the methods you're interested in.
(有时，您可能希望观察智能体的生命周期。例如，您可能希望记录事件，或在某些事件发生时预取数据。您可以使用`hooks`属性挂钩到智能体生命周期中。子类化[`AgentHooks`][agents.lifecycle.AgentHooks]类，并重写您感兴趣的方法。)

## Guardrails (防护栏)

Guardrails allow you to run checks/validations on user input, in parallel to the agent running. For example, you could screen the user's input for relevance. Read more in the [guardrails](guardrails.md) documentation.
(防护栏允许您在智能体运行的同时对用户输入进行检查/验证。例如，您可以筛选用户输入的相关性。更多信息请参阅[防护栏](guardrails.md)文档。)

## Cloning/copying agents (克隆/复制智能体)

By using the `clone()` method on an agent, you can duplicate an Agent, and optionally change any properties you like.
(通过在智能体上使用`clone()`方法，您可以复制一个智能体，并可选地更改您喜欢的任何属性。)

```python
pirate_agent = Agent(
    name="Pirate",
    instructions="Write like a pirate",
    model="o3-mini",
)

robot_agent = pirate_agent.clone(
    name="Robot",
    instructions="Write like a robot",
)
```

## Forcing tool use (强制工具使用)

Supplying a list of tools doesn't always mean the LLM will use a tool. You can force tool use by setting [`ModelSettings.tool_choice`][agents.model_settings.ModelSettings.tool_choice]. Valid values are:
(提供工具列表并不总是意味着LLM会使用工具。您可以通过设置[`ModelSettings.tool_choice`][agents.model_settings.ModelSettings.tool_choice]来强制使用工具。有效值为：)

1. `auto`, which allows the LLM to decide whether or not to use a tool.
   (`auto`，允许LLM决定是否使用工具。)
2. `required`, which requires the LLM to use a tool (but it can intelligently decide which tool).
   (`required`，要求LLM必须使用工具(但可以智能地决定使用哪个工具)。)
3. `none`, which requires the LLM to _not_ use a tool.
   (`none`，要求LLM不使用工具。)
4. Setting a specific string e.g. `my_tool`, which requires the LLM to use that specific tool.
   (设置特定字符串如`my_tool`，要求LLM使用该特定工具。)

!!! note

    To prevent infinite loops, the framework automatically resets `tool_choice` to "auto" after a tool call. This behavior is configurable via [`agent.reset_tool_choice`][agents.agent.Agent.reset_tool_choice]. The infinite loop is because tool results are sent to the LLM, which then generates another tool call because of `tool_choice`, ad infinitum.
    (为了防止无限循环，框架在工具调用后自动将`tool_choice`重置为"auto"。此行为可通过[`agent.reset_tool_choice`][agents.agent.Agent.reset_tool_choice]配置。无限循环是因为工具结果被发送给LLM，然后由于`tool_choice`而生成另一个工具调用，如此循环往复。)

    If you want the Agent to completely stop after a tool call (rather than continuing with auto mode), you can set [`Agent.tool_use_behavior="stop_on_first_tool"`] which will directly use the tool output as the final response without further LLM processing.
    (如果您希望智能体在工具调用后完全停止(而不是继续自动模式)，可以设置[`Agent.tool_use_behavior="stop_on_first_tool"`]，这将直接使用工具输出作为最终响应，而不进行进一步的LLM处理。)
