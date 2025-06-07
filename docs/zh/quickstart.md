# Quickstart （快速入门）

## Create a project and virtual environment （创建项目和虚拟环境）

You'll only need to do this once.
（只需执行一次）

```bash
mkdir my_project
cd my_project
python -m venv .venv
```

### Activate the virtual environment （激活虚拟环境）

Do this every time you start a new terminal session.
（每次开启新的终端会话时都需要执行）

```bash
source .venv/bin/activate
```

### Install the Agents SDK （安装Agents SDK）

```bash
pip install openai-agents # or `uv add openai-agents`, etc
```

### Set an OpenAI API key （设置OpenAI API密钥）

If you don't have one, follow [these instructions](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key) to create an OpenAI API key.
（如果没有API密钥，请按照[这些说明](https://platform.openai.com/docs/quickstart#create-and-export-an-api-key)创建）

```bash
export OPENAI_API_KEY=sk-...
```

## Create your first agent （创建第一个智能体）

Agents are defined with instructions, a name, and optional config (such as `model_config`)
（智能体通过指令、名称和可选配置（如`model_config`）定义）

```python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

## Add a few more agents （添加更多智能体）

Additional agents can be defined in the same way. `handoff_descriptions` provide additional context for determining handoff routing
（可以同样方式定义更多智能体。`handoff_descriptions`为交接路由提供额外上下文）

```python
from agents import Agent

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)
```

## Define your handoffs （定义交接）

On each agent, you can define an inventory of outgoing handoff options that the agent can choose from to decide how to make progress on their task.
（在每个智能体上，可以定义一组交接选项供其选择以决定如何推进任务）

```python
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)
```

## Run the agent orchestration （运行智能体编排）

Let's check that the workflow runs and the triage agent correctly routes between the two specialist agents.
（让我们检查工作流是否正常运行，以及分诊智能体能否正确在两个专业智能体间路由）

```python
from agents import Runner

async def main():
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)
```

## Add a guardrail （添加防护栏）

You can define custom guardrails to run on the input or output.
（可以定义在输入或输出上运行的自定义防护栏）

```python
from agents import GuardrailFunctionOutput, Agent, Runner
from pydantic import BaseModel

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )
```

## Put it all together （整合所有内容）

Let's put it all together and run the entire workflow, using handoffs and the input guardrail.
（让我们整合所有内容并运行完整工作流，使用交接和输入防护栏）

```python
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput,
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)


async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail),
    ],
)

async def main():
    result = await Runner.run(triage_agent, "who was the first president of the united states?")
    print(result.final_output)

    result = await Runner.run(triage_agent, "what is life")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## View your traces （查看追踪记录）

To review what happened during your agent run, navigate to the [Trace viewer in the OpenAI Dashboard](https://platform.openai.com/traces) to view traces of your agent runs.
（要查看智能体运行期间发生的情况，请导航至[OpenAI仪表板中的追踪查看器](https://platform.openai.com/traces)查看智能体运行的追踪记录）

## Next steps （后续步骤）

Learn how to build more complex agentic flows:
（学习如何构建更复杂的智能体流程：）

-   Learn about how to configure [Agents](agents.md). （学习如何配置[智能体](agents.md)）
-   Learn about [running agents](running_agents.md). （学习[运行智能体](running_agents.md)）
-   Learn about [tools](tools.md), [guardrails](guardrails.md) and [models](models/index.md). （学习[工具](tools.md)、[防护栏](guardrails.md)和[模型](models/index.md)）
