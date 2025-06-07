# OpenAI智能体SDK

[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)让你能够以轻量级、易用且抽象极少的方式构建智能AI应用。它是我们之前智能体实验项目[Swarm](https://github.com/openai/swarm/tree/main)的生产就绪升级版。该智能体SDK提供了一组非常精简的基础组件:

-   **Agents**，`智能体`即配备了指令和工具的大语言模型
-   **Handoffs**，`交接`允许智能体将特定任务委托给其他智能体
-   **Guardrails**，`防护栏`用于验证智能体的输入

结合Python使用，这些基础组件足以表达工具和智能体之间的复杂关系，让你能够构建真实世界的应用而无需陡峭的学习曲线。此外，该SDK还内置了**追踪**功能，让你可以可视化和调试智能体流程，以及评估它们甚至为你的应用微调模型。

## 为什么使用智能体SDK

该SDK有两个核心设计原则:

1. 功能足够丰富值得使用，但基础组件足够少以便快速学习。
2. 开箱即用效果良好，但你可以精确自定义行为。

以下是该SDK的主要功能:

-   Agent loop: `智能体循环`内置的智能体循环，处理工具调用、将结果发送给大语言模型，并循环直到大语言模型完成。
-   Python-first: `Python优先`使用内置语言特性来编排和链式调用智能体，而无需学习新的抽象概念。
-   Handoffs: `交接`在多个智能体之间协调和委托的强大功能。
-   Guardrails: `防护栏`与智能体并行运行输入验证和检查，如果检查失败则提前终止。
-   Function tools: `函数工具`将任何Python函数转换为工具，具有自动模式生成和Pydantic驱动的验证功能。
-   Tracing: `追踪`内置的追踪功能，让你可以可视化、调试和监控工作流，以及使用OpenAI的评估、微调和蒸馏工具套件。

## 安装

```bash
pip install openai-agents
```

## Hello world示例

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

运行此代码前，请确保设置了`OPENAI_API_KEY`环境变量

```bash
export OPENAI_API_KEY=sk-...
```
