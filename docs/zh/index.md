# OpenAI Agents SDK (OpenAI智能体SDK)

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) enables you to build agentic AI apps in a lightweight, easy-to-use package with very few abstractions. It's a production-ready upgrade of our previous experimentation for agents, [Swarm](https://github.com/openai/swarm/tree/main). The Agents SDK has a very small set of primitives:
([OpenAI Agents SDK](https://github.com/openai/openai-agents-python)让你能够以轻量级、易用且抽象极少的方式构建智能AI应用。它是我们之前智能体实验项目[Swarm](https://github.com/openai/swarm/tree/main)的生产就绪升级版。该智能体SDK提供了一组非常精简的基础组件:)

-   **Agents**, which are LLMs equipped with instructions and tools
(**智能体**，即配备了指令和工具的大语言模型)
-   **Handoffs**, which allow agents to delegate to other agents for specific tasks
(**交接**，允许智能体将特定任务委托给其他智能体)
-   **Guardrails**, which enable the inputs to agents to be validated
(**防护栏**，用于验证智能体的输入)

In combination with Python, these primitives are powerful enough to express complex relationships between tools and agents, and allow you to build real-world applications without a steep learning curve. In addition, the SDK comes with built-in **tracing** that lets you visualize and debug your agentic flows, as well as evaluate them and even fine-tune models for your application.
(结合Python使用，这些基础组件足以表达工具和智能体之间的复杂关系，让你能够构建真实世界的应用而无需陡峭的学习曲线。此外，该SDK还内置了**追踪**功能，让你可以可视化和调试智能体流程，以及评估它们甚至为你的应用微调模型。)

## Why use the Agents SDK (为什么使用智能体SDK)

The SDK has two driving design principles:
(该SDK有两个核心设计原则:)

1. Enough features to be worth using, but few enough primitives to make it quick to learn.
(功能足够丰富值得使用，但基础组件足够少以便快速学习。)
2. Works great out of the box, but you can customize exactly what happens.
(开箱即用效果良好，但你可以精确自定义行为。)

Here are the main features of the SDK:
(以下是该SDK的主要功能:)

-   Agent loop: Built-in agent loop that handles calling tools, sending results to the LLM, and looping until the LLM is done.
(智能体循环：内置的智能体循环，处理工具调用、将结果发送给大语言模型，并循环直到大语言模型完成。)
-   Python-first: Use built-in language features to orchestrate and chain agents, rather than needing to learn new abstractions.
(Python优先：使用内置语言特性来编排和链式调用智能体，而无需学习新的抽象概念。)
-   Handoffs: A powerful feature to coordinate and delegate between multiple agents.
(交接：在多个智能体之间协调和委托的强大功能。)
-   Guardrails: Run input validations and checks in parallel to your agents, breaking early if the checks fail.
(防护栏：与智能体并行运行输入验证和检查，如果检查失败则提前终止。)
-   Function tools: Turn any Python function into a tool, with automatic schema generation and Pydantic-powered validation.
(函数工具：将任何Python函数转换为工具，具有自动模式生成和Pydantic驱动的验证功能。)
-   Tracing: Built-in tracing that lets you visualize, debug and monitor your workflows, as well as use the OpenAI suite of evaluation, fine-tuning and distillation tools.
(追踪：内置的追踪功能，让你可以可视化、调试和监控工作流，以及使用OpenAI的评估、微调和蒸馏工具套件。)

## Installation (安装)

```bash
pip install openai-agents
```

## Hello world example (Hello world示例)

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

(_If running this, ensure you set the `OPENAI_API_KEY` environment variable_)
(运行此代码前，请确保设置了`OPENAI_API_KEY`环境变量)

```bash
export OPENAI_API_KEY=sk-...
```
