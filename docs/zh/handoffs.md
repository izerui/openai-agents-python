# Handoffs (交接)

Handoffs allow an agent to delegate tasks to another agent. This is particularly useful in scenarios where different agents specialize in distinct areas. For example, a customer support app might have agents that each specifically handle tasks like order status, refunds, FAQs, etc.
(交接允许一个智能体将任务委托给另一个智能体。这在不同的智能体专长于不同领域的场景中特别有用。例如，一个客户支持应用可能有专门处理订单状态、退款、常见问题等不同任务的智能体。)

Handoffs are represented as tools to the LLM. So if there's a handoff to an agent named `Refund Agent`, the tool would be called `transfer_to_refund_agent`.
(交接对大语言模型表示为工具。因此，如果有一个名为`Refund Agent`的交接，对应的工具将被称为`transfer_to_refund_agent`。)

## Creating a handoff (创建交接)

All agents have a [`handoffs`][agents.agent.Agent.handoffs] param, which can either take an `Agent` directly, or a `Handoff` object that customizes the Handoff.
(所有智能体都有一个[`handoffs`][agents.agent.Agent.handoffs]参数，可以直接接收一个`Agent`，或者一个自定义交接的`Handoff`对象。)

You can create a handoff using the [`handoff()`][agents.handoffs.handoff] function provided by the Agents SDK. This function allows you to specify the agent to hand off to, along with optional overrides and input filters.
(你可以使用Agents SDK提供的[`handoff()`][agents.handoffs.handoff]函数创建交接。这个函数允许你指定要交接的智能体，以及可选的覆盖和输入过滤器。)

### Basic Usage (基本用法)

Here's how you can create a simple handoff:
(以下是创建简单交接的方法:)

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

# (1)!
triage_agent = Agent(name="Triage agent", handoffs=[billing_agent, handoff(refund_agent)])
```

1. You can use the agent directly (as in `billing_agent`), or you can use the `handoff()` function.
(你可以直接使用智能体(如`billing_agent`)，或者使用`handoff()`函数。)

### Customizing handoffs via the `handoff()` function (通过`handoff()`函数自定义交接)

The [`handoff()`][agents.handoffs.handoff] function lets you customize things.
([`handoff()`][agents.handoffs.handoff]函数允许你自定义以下内容:)

-   `agent`: This is the agent to which things will be handed off.
(这是要交接到的智能体。)
-   `tool_name_override`: By default, the `Handoff.default_tool_name()` function is used, which resolves to `transfer_to_<agent_name>`. You can override this.
(默认使用`Handoff.default_tool_name()`函数，解析为`transfer_to_<agent_name>`。你可以覆盖此名称。)
-   `tool_description_override`: Override the default tool description from `Handoff.default_tool_description()`
(覆盖`Handoff.default_tool_description()`的默认工具描述。)
-   `on_handoff`: A callback function executed when the handoff is invoked. This is useful for things like kicking off some data fetching as soon as you know a handoff is being invoked. This function receives the agent context, and can optionally also receive LLM generated input. The input data is controlled by the `input_type` param.
(交接被调用时执行的回调函数。这在需要立即启动数据获取等操作时很有用。该函数接收智能体上下文，并可选择接收LLM生成的输入。输入数据由`input_type`参数控制。)
-   `input_type`: The type of input expected by the handoff (optional).
(交接期望的输入类型(可选)。)
-   `input_filter`: This lets you filter the input received by the next agent. See below for more.
(这允许你过滤下一个智能体接收的输入。详见下文。)

```python
from agents import Agent, handoff, RunContextWrapper

def on_handoff(ctx: RunContextWrapper[None]):
    print("Handoff called")

agent = Agent(name="My agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    tool_name_override="custom_handoff_tool",
    tool_description_override="Custom description",
)
```

## Handoff inputs (交接输入)

In certain situations, you want the LLM to provide some data when it calls a handoff. For example, imagine a handoff to an "Escalation agent". You might want a reason to be provided, so you can log it.
(在某些情况下，你希望LLM在调用交接时提供一些数据。例如，想象一个交接给"升级处理智能体"的场景。你可能希望提供一个原因，以便记录。)

```python
from pydantic import BaseModel

from agents import Agent, handoff, RunContextWrapper

class EscalationData(BaseModel):
    reason: str

async def on_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    print(f"Escalation agent called with reason: {input_data.reason}")

agent = Agent(name="Escalation agent")

handoff_obj = handoff(
    agent=agent,
    on_handoff=on_handoff,
    input_type=EscalationData,
)
```
(这段代码展示了如何定义一个包含原因字段的基础模型，并在交接回调中打印出升级原因。)

## Input filters (输入过滤器)

When a handoff occurs, it's as though the new agent takes over the conversation, and gets to see the entire previous conversation history. If you want to change this, you can set an [`input_filter`][agents.handoffs.Handoff.input_filter]. An input filter is a function that receives the existing input via a [`HandoffInputData`][agents.handoffs.HandoffInputData], and must return a new `HandoffInputData`.
(当交接发生时，新的智能体会接管对话，并可以看到整个先前的对话历史。如果你想改变这一点，可以设置一个[`input_filter`][agents.handoffs.Handoff.input_filter]。输入过滤器是一个函数，它通过[`HandoffInputData`][agents.handoffs.HandoffInputData]接收现有输入，并必须返回一个新的`HandoffInputData`。)

There are some common patterns (for example removing all tool calls from the history), which are implemented for you in [`agents.extensions.handoff_filters`][]
(有一些常见模式(例如从历史记录中删除所有工具调用)已经在[`agents.extensions.handoff_filters`][]中为你实现。)

```python
from agents import Agent, handoff
from agents.extensions import handoff_filters

agent = Agent(name="FAQ agent")

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools, # (1)!
)
```

1. This will automatically remove all tools from the history when `FAQ agent` is called.
(这将在调用`FAQ agent`时自动从历史记录中删除所有工具。)

## Recommended prompts (推荐提示词)

To make sure that LLMs understand handoffs properly, we recommend including information about handoffs in your agents. We have a suggested prefix in [`agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX`][], or you can call [`agents.extensions.handoff_prompt.prompt_with_handoff_instructions`][] to automatically add recommended data to your prompts.
(为了确保LLM正确理解交接，我们建议在你的智能体中包含关于交接的信息。我们在[`agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX`][]中提供了一个建议的前缀，或者你可以调用[`agents.extensions.handoff_prompt.prompt_with_handoff_instructions`][]自动将推荐数据添加到你的提示词中。)

```python
from agents import Agent
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

billing_agent = Agent(
    name="Billing agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    <Fill in the rest of your prompt here>.""",
)
```
(这段代码展示了如何在账单智能体的提示词中包含推荐的交接前缀。)
