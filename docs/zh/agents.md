# 智能体

智能体是应用程序中的核心构建模块。一个智能体是一个配置了指令和工具的大型语言模型(LLM)。

## 基础配置

智能体最常配置的属性包括：

- `instructions`: 也称为开发者消息或系统提示
- `model`: 使用的LLM模型，以及可选的`model_settings`用于配置模型调优参数如temperature、top_p等
- `tools`: 智能体可用于完成任务的各种工具

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

## Context

智能体的`context`类型是泛型的。上下文是一个依赖注入工具：它是你创建并传递给`Runner.run()`的对象，会传递给每个智能体、工具、交接等，作为智能体运行的依赖和状态的容器。你可以提供任何Python对象作为上下文。

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

## 输出类型

默认情况下，智能体产生纯文本(即`str`)输出。如果你希望智能体产生特定类型的输出，可以使用`output_type`参数。常见的选择是使用[Pydantic](https://docs.pydantic.dev/)对象，但我们支持任何可以用Pydantic [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/)包装的类型 - 数据类、列表、TypedDict等。

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

    当你传递`output_type`时，这会告诉模型使用[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)而不是常规的纯文本响应。

## Handoffs

`Handoffs`是智能体可以委托的子智能体。你提供一个交接列表，智能体可以在相关时选择委托给它们。这是一种强大的模式，可以协调模块化、专业化的智能体，每个智能体都擅长单一任务。更多信息请参

阅[交接](handoffs.md)文档。

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

## 动态指令

在大多数情况下，你可以在创建智能体时提供指令。但是，你也可以通过函数提供动态指令。该函数将接收智能体和上下文，并必须返回提示。支持常规函数和`async`函数。

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

## 生命周期事件(钩子)

有时，你可能想要观察智能体的生命周期。例如，你可能想要记录事件，或在某些事件发生时预取数据。你可以通过`hooks`属性钩入智能体生命周期。子类化[`AgentHooks`][agents.lifecycle.AgentHooks]类，并重写你感兴趣的方法。

## 防护栏

防护栏允许你在智能体运行的同时对用户输入运行检查/验证。例如，你可以筛选用户输入的相关性。更多信息请参阅[防护栏](guardrails.md)文档。

## 克隆/复制智能体

通过在智能体上使用`clone()`方法，你可以复制一个智能体，并可选地更改任何你想要的属性。

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

## 强制使用工具

提供工具列表并不总是意味着LLM会使用工具。你可以通过设置[`ModelSettings.tool_choice`][agents.model_settings.ModelSettings.tool_choice]来强制使用工具。有效值为：

1. `auto`，允许LLM决定是否使用工具
2. `required`，要求LLM必须使用工具(但可以智能地决定使用哪个工具)
3. `none`，要求LLM不使用工具
4. 设置特定字符串如`my_tool`，要求LLM必须使用该特定工具

!!! note

    为了防止无限循环，框架在工具调用后会自动将`tool_choice`重置为"auto"。这种行为可以通过[`agent.reset_tool_choice`][agents.agent.Agent.reset_tool_choice]配置。无限循环是因为工具结果被发送给LLM，然后由于`tool_choice`又生成另一个工具调用，如此循环往复。

    如果你希望智能体在工具调用后完全停止(而不是继续使用自动模式)，你可以设置[`Agent.tool_use_behavior="stop_on_first_tool"`]，这将直接使用工具输出作为最终响应，而不进行进一步的LLM处理。
