# 防护栏(Guardrails)

防护栏与您的智能体_并行_运行，使您能够对用户输入进行检查和验证。例如，假设您有一个使用非常智能(因此速度慢/成本高)模型的智能体来处理客户请求。您不会希望恶意用户让模型帮他们做数学作业。这时，您可以运行一个快速/廉价的防护栏模型。如果防护栏检测到恶意使用，它可以立即引发错误，从而阻止昂贵模型的运行，节省您的时间和金钱。

防护栏有两种类型：

1. 输入防护栏 - 在初始用户输入时运行
2. 输出防护栏 - 在最终智能体输出时运行

## 输入防护栏

输入防护栏分3个步骤运行：

1. 首先，防护栏接收与传递给智能体相同的输入
2. 接着，运行防护栏函数生成[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]，然后将其包装在[`InputGuardrailResult`][agents.guardrail.InputGuardrailResult]中
3. 最后，检查[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]是否为true。如果为true，则引发[`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered]异常，以便您可以适当地响应用户或处理异常。

!!! Note

    输入防护栏旨在对用户输入运行，因此只有当智能体是_第一个_智能体时才会运行其防护栏。您可能会疑惑，为什么`guardrails`属性放在智能体上而不是传递给`Runner.run`？这是因为防护栏往往与实际智能体相关 - 您会为不同的智能体运行不同的防护栏，因此将代码放在一起有助于提高可读性。

## 输出防护栏

输出防护栏分3个步骤运行：

1. 首先，防护栏接收与传递给智能体相同的输入
2. 接着，运行防护栏函数生成[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]，然后将其包装在[`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult]中
3. 最后，检查[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]是否为true。如果为true，则引发[`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered]异常，以便您可以适当地响应用户或处理异常。

!!! Note

    输出防护栏旨在对最终智能体输出运行，因此只有当智能体是_最后一个_智能体时才会运行其防护栏。与输入防护栏类似，我们这样做是因为防护栏往往与实际智能体相关 - 您会为不同的智能体运行不同的防护栏，因此将代码放在一起有助于提高可读性。

## 触发机制(Tripwires)

如果输入或输出未通过防护栏检查，防护栏可以通过触发机制发出信号。一旦我们看到防护栏触发了触发机制，我们会立即引发`{Input,Output}GuardrailTripwireTriggered`异常并停止智能体执行。

## 实现防护栏

您需要提供一个接收输入并返回[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]的函数。在这个例子中，我们将通过运行一个底层智能体来实现。

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent( # (1)!
    name="防护栏检查",
    instructions="检查用户是否在要求你帮他们做数学作业。",
    output_type=MathHomeworkOutput,
)


@input_guardrail
async def math_guardrail( # (2)!
    ctx: RunContextWrapper[None], agent: Agent, input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output, # (3)!
        tripwire_triggered=result.final_output.is_math_homework,
    )


agent = Agent(  # (4)!
    name="客户支持智能体",
    instructions="你是一个客户支持智能体。你帮助客户解答问题。",
    input_guardrails=[math_guardrail],
)

async def main():
    # 这会触发防护栏
    try:
        await Runner.run(agent, "你好，你能帮我解这个方程吗：2x + 3 = 11?")
        print("防护栏未触发 - 这不符合预期")

    except InputGuardrailTripwireTriggered:
        print("数学作业防护栏已触发")
```

1. 我们将在防护栏函数中使用这个智能体。
2. 这是接收智能体输入/上下文并返回结果的防护栏函数。
3. 我们可以在防护栏结果中包含额外信息。
4. 这是定义工作流程的实际智能体。

输出防护栏类似。

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)
class MessageOutput(BaseModel): # (1)!
    response: str

class MathOutput(BaseModel): # (2)!
    reasoning: str
    is_math: bool

guardrail_agent = Agent(
    name="防护栏检查",
    instructions="检查输出是否包含任何数学内容。",
    output_type=MathOutput,
)

@output_guardrail
async def math_guardrail(  # (3)!
    ctx: RunContextWrapper, agent: Agent, output: MessageOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, output.response, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math,
    )

agent = Agent( # (4)!
    name="客户支持智能体",
    instructions="你是一个客户支持智能体。你帮助客户解答问题。",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # 这会触发防护栏
    try:
        await Runner.run(agent, "你好，你能帮我解这个方程吗：2x + 3 = 11?")
        print("防护栏未触发 - 这不符合预期")

    except OutputGuardrailTripwireTriggered:
        print("数学输出防护栏已触发")
```

1. 这是实际智能体的输出类型。
2. 这是防护栏的输出类型。
3. 这是接收智能体输出并返回结果的防护栏函数。
4. 这是定义工作流程的实际智能体。
