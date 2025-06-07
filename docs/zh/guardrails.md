# Guardrails (防护栏)

Guardrails run _in parallel_ to your agents, enabling you to do checks and validations of user input. For example, imagine you have an agent that uses a very smart (and hence slow/expensive) model to help with customer requests. You wouldn't want malicious users to ask the model to help them with their math homework. So, you can run a guardrail with a fast/cheap model. If the guardrail detects malicious usage, it can immediately raise an error, which stops the expensive model from running and saves you time/money.
(防护栏与您的智能体_并行_运行，使您能够对用户输入进行检查和验证。例如，假设您有一个使用非常智能(因此速度慢/成本高)的模型来帮助处理客户请求的智能体。您不希望恶意用户让模型帮助他们做数学作业。因此，您可以运行一个使用快速/廉价模型的防护栏。如果防护栏检测到恶意使用，它可以立即引发错误，从而阻止昂贵模型的运行，节省您的时间和金钱。)

There are two kinds of guardrails:
(防护栏有两种类型：)

1. Input guardrails run on the initial user input
   (输入防护栏在初始用户输入上运行)
2. Output guardrails run on the final agent output
   (输出防护栏在最终智能体输出上运行)

## Input guardrails (输入防护栏)

Input guardrails run in 3 steps:
(输入防护栏分3步运行：)

1. First, the guardrail receives the same input passed to the agent.
   (首先，防护栏接收传递给智能体的相同输入。)
2. Next, the guardrail function runs to produce a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput], which is then wrapped in an [`InputGuardrailResult`][agents.guardrail.InputGuardrailResult]
   (接下来，防护栏函数运行生成[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]，然后将其包装在[`InputGuardrailResult`][agents.guardrail.InputGuardrailResult]中)
3. Finally, we check if [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] is true. If true, an [`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered] exception is raised, so you can appropriately respond to the user or handle the exception.
   (最后，我们检查[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]是否为true。如果为true，则引发[`InputGuardrailTripwireTriggered`][agents.exceptions.InputGuardrailTripwireTriggered]异常，以便您可以适当地响应用户或处理异常。)

!!! Note
(!!! 注意)

    Input guardrails are intended to run on user input, so an agent's guardrails only run if the agent is the *first* agent. You might wonder, why is the `guardrails` property on the agent instead of passed to `Runner.run`? It's because guardrails tend to be related to the actual Agent - you'd run different guardrails for different agents, so colocating the code is useful for readability.
    (输入防护栏旨在对用户输入运行，因此只有当智能体是*第一个*智能体时才会运行其防护栏。您可能会想，为什么`guardrails`属性放在智能体上而不是传递给`Runner.run`？这是因为防护栏往往与实际智能体相关 - 您会为不同的智能体运行不同的防护栏，因此将代码放在一起有助于提高可读性。)

## Output guardrails (输出防护栏)

Output guardrails run in 3 steps:
(输出防护栏分3步运行：)

1. First, the guardrail receives the same input passed to the agent.
   (首先，防护栏接收传递给智能体的相同输入。)
2. Next, the guardrail function runs to produce a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput], which is then wrapped in an [`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult]
   (接下来，防护栏函数运行生成[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]，然后将其包装在[`OutputGuardrailResult`][agents.guardrail.OutputGuardrailResult]中)
3. Finally, we check if [`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered] is true. If true, an [`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered] exception is raised, so you can appropriately respond to the user or handle the exception.
   (最后，我们检查[`.tripwire_triggered`][agents.guardrail.GuardrailFunctionOutput.tripwire_triggered]是否为true。如果为true，则引发[`OutputGuardrailTripwireTriggered`][agents.exceptions.OutputGuardrailTripwireTriggered]异常，以便您可以适当地响应用户或处理异常。)

!!! Note
(!!! 注意)

    Output guardrails are intended to run on the final agent output, so an agent's guardrails only run if the agent is the *last* agent. Similar to the input guardrails, we do this because guardrails tend to be related to the actual Agent - you'd run different guardrails for different agents, so colocating the code is useful for readability.
    (输出防护栏旨在对最终智能体输出运行，因此只有当智能体是*最后一个*智能体时才会运行其防护栏。与输入防护栏类似，我们这样做是因为防护栏往往与实际智能体相关 - 您会为不同的智能体运行不同的防护栏，因此将代码放在一起有助于提高可读性。)

## Tripwires (触发机制)

If the input or output fails the guardrail, the Guardrail can signal this with a tripwire. As soon as we see a guardrail that has triggered the tripwires, we immediately raise a `{Input,Output}GuardrailTripwireTriggered` exception and halt the Agent execution.
(如果输入或输出未通过防护栏检查，防护栏可以通过触发机制发出信号。一旦我们看到防护栏触发了触发机制，我们立即引发`{Input,Output}GuardrailTripwireTriggered`异常并停止智能体执行。)

## Implementing a guardrail (实现防护栏)

You need to provide a function that receives input, and returns a [`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]. In this example, we'll do this by running an Agent under the hood.
(您需要提供一个接收输入并返回[`GuardrailFunctionOutput`][agents.guardrail.GuardrailFunctionOutput]的函数。在这个例子中，我们将通过运行一个智能体来实现这一点。)

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
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
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
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[math_guardrail],
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except InputGuardrailTripwireTriggered:
        print("Math homework guardrail tripped")
```

1. We'll use this agent in our guardrail function.
   (我们将在防护栏函数中使用这个智能体。)
2. This is the guardrail function that receives the agent's input/context, and returns the result.
   (这是接收智能体输入/上下文并返回结果的防护栏函数。)
3. We can include extra information in the guardrail result.
   (我们可以在防护栏结果中包含额外信息。)
4. This is the actual agent that defines the workflow.
   (这是定义工作流的实际智能体。)

Output guardrails are similar.
(输出防护栏类似。)

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
    name="Guardrail check",
    instructions="Check if the output includes any math.",
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
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    output_guardrails=[math_guardrail],
    output_type=MessageOutput,
)

async def main():
    # This should trip the guardrail
    try:
        await Runner.run(agent, "Hello, can you help me solve for x: 2x + 3 = 11?")
        print("Guardrail didn't trip - this is unexpected")

    except OutputGuardrailTripwireTriggered:
        print("Math output guardrail tripped")
```

1. This is the actual agent's output type.
   (这是实际智能体的输出类型。)
2. This is the guardrail's output type.
   (这是防护栏的输出类型。)
3. This is the guardrail function that receives the agent's output, and returns the result.
   (这是接收智能体输出并返回结果的防护栏函数。)
4. This is the actual agent that defines the workflow.
   (这是定义工作流的实际智能体。)
