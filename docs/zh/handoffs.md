# 交接

交接允许一个智能体将任务委托给另一个智能体。这在不同的智能体专长于不同领域的场景中特别有用。例如，一个客户支持应用可能有专门处理订单状态、退款、常见问题等不同任务的智能体。

交接对大语言模型表示为工具。因此，如果有一个名为`Refund Agent`的交接，对应的工具将被称为`transfer_to_refund_agent`。

## 创建交接

所有智能体都有一个[`handoffs`][agents.agent.Agent.handoffs]参数，可以直接接收一个`Agent`，或者一个自定义交接的`Handoff`对象。

你可以使用Agents SDK提供的[`handoff()`][agents.handoffs.handoff]函数创建交接。这个函数允许你指定要交接的智能体，以及可选的覆盖和输入过滤器。

### 基本用法

以下是创建简单交接的方法:

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing agent")
refund_agent = Agent(name="Refund agent")

# (1)!
triage_agent = Agent(name="Triage agent", handoffs=[billing_agent, handoff(refund_agent)])
```

1. 你可以直接使用智能体(如`billing_agent`)，或者使用`handoff()`函数。

### 通过`handoff()`函数自定义交接

[`handoff()`][agents.handoffs.handoff]函数允许你自定义以下内容:

-   `agent`: 这是要交接到的智能体。
-   `tool_name_override`: 默认使用`Handoff.default_tool_name()`函数，解析为`transfer_to_<agent_name>`。你可以覆盖此名称。
-   `tool_description_override`: 覆盖`Handoff.default_tool_description()`的默认工具描述。
-   `on_handoff`: 交接被调用时执行的回调函数。这在需要立即启动数据获取等操作时很有用。该函数接收智能体上下文，并可选择接收LLM生成的输入。输入数据由`input_type`参数控制。
-   `input_type`: 交接期望的输入类型(可选)。
-   `input_filter`: 这允许你过滤下一个智能体接收的输入。详见下文。

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

## 交接输入

在某些情况下，你希望LLM在调用交接时提供一些数据。例如，想象一个交接给"升级处理智能体"的场景。你可能希望提供一个原因，以便记录。

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

## 输入过滤器

当交接发生时，新的智能体会接管对话，并可以看到整个先前的对话历史。如果你想改变这一点，可以设置一个[`input_filter`][agents.handoffs.Handoff.input_filter]。输入过滤器是一个函数，它通过[`HandoffInputData`][agents.handoffs.HandoffInputData]接收现有输入，并必须返回一个新的`HandoffInputData`。

有一些常见模式(例如从历史记录中删除所有工具调用)已经在[`agents.extensions.handoff_filters`][]中为你实现。

```python
from agents import Agent, handoff
from agents.extensions import handoff_filters

agent = Agent(name="FAQ agent")

handoff_obj = handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools, # (1)!
)
```

1. 这将在调用`FAQ agent`时自动从历史记录中删除所有工具。

## 推荐提示词

为了确保LLM正确理解交接，我们建议在你的智能体中包含关于交接的信息。我们在[`agents.extensions.handoff_prompt.RECOMMENDED_PROMPT_PREFIX`][]中提供了一个建议的前缀，或者你可以调用[`agents.extensions.handoff_prompt.prompt_with_handoff_instructions`][]自动将推荐数据添加到你的提示词中。

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
