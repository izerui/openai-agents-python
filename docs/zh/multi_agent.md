# Orchestrating multiple agents
（编排多个智能体）

Orchestration refers to the flow of agents in your app. Which agents run, in what order, and how do they decide what happens next? There are two main ways to orchestrate agents:
（编排指的是应用中智能体的流程。哪些智能体运行、以什么顺序运行，以及它们如何决定下一步要做什么？主要有两种编排智能体的方式：）

1. Allowing the LLM to make decisions: this uses the intelligence of an LLM to plan, reason, and decide on what steps to take based on that.
（1. 让LLM做决策：利用LLM的智能来规划、推理并决定采取哪些步骤）
2. Orchestrating via code: determining the flow of agents via your code.
（2. 通过代码编排：通过代码确定智能体的流程）

You can mix and match these patterns. Each has their own tradeoffs, described below.
（你可以混合使用这些模式。每种模式都有其权衡取舍，如下所述。）

## Orchestrating via LLM
（通过LLM编排）

An agent is an LLM equipped with instructions, tools and handoffs. This means that given an open-ended task, the LLM can autonomously plan how it will tackle the task, using tools to take actions and acquire data, and using handoffs to delegate tasks to sub-agents. For example, a research agent could be equipped with tools like:
（智能体是配备了指令、工具和交接的LLM。这意味着给定一个开放式任务，LLM可以自主规划如何完成任务，使用工具采取行动和获取数据，并使用交接将任务委托给子智能体。例如，一个研究智能体可以配备以下工具：）

-   Web search to find information online
（- 网络搜索以在线查找信息）
-   File search and retrieval to search through proprietary data and connections
（- 文件搜索和检索以搜索专有数据和连接）
-   Computer use to take actions on a computer
（- 计算机使用以在计算机上执行操作）
-   Code execution to do data analysis
（- 代码执行以进行数据分析）
-   Handoffs to specialized agents that are great at planning, report writing and more.
（- 交接给擅长规划、报告撰写等的专业智能体）

This pattern is great when the task is open-ended and you want to rely on the intelligence of an LLM. The most important tactics here are:
（当任务是开放式的并且你想依赖LLM的智能时，这种模式非常有用。最重要的策略是：）

1. Invest in good prompts. Make it clear what tools are available, how to use them, and what parameters it must operate within.
（1. 投入好的提示。明确说明可用的工具、如何使用它们以及它必须在哪些参数范围内操作）
2. Monitor your app and iterate on it. See where things go wrong, and iterate on your prompts.
（2. 监控你的应用并迭代。看看哪里出了问题，并迭代你的提示）
3. Allow the agent to introspect and improve. For example, run it in a loop, and let it critique itself; or, provide error messages and let it improve.
（3. 允许智能体自省和改进。例如，在循环中运行它，让它自我批评；或者提供错误消息让它改进）
4. Have specialized agents that excel in one task, rather than having a general purpose agent that is expected to be good at anything.
（4. 拥有擅长一项任务的专门智能体，而不是期望一个通用智能体擅长任何事情）
5. Invest in [evals](https://platform.openai.com/docs/guides/evals). This lets you train your agents to improve and get better at tasks.
（5. 投入[评估](https://platform.openai.com/docs/guides/evals)。这让你可以训练你的智能体改进并更好地完成任务）

## Orchestrating via code
（通过代码编排）

While orchestrating via LLM is powerful, orchestrating via code makes tasks more deterministic and predictable, in terms of speed, cost and performance. Common patterns here are:
（虽然通过LLM编排很强大，但通过代码编排使任务在速度、成本和性能方面更加确定和可预测。常见的模式有：）

-   Using [structured outputs](https://platform.openai.com/docs/guides/structured-outputs) to generate well formed data that you can inspect with your code. For example, you might ask an agent to classify the task into a few categories, and then pick the next agent based on the category.
（- 使用[结构化输出](https://platform.openai.com/docs/guides/structured-outputs)生成格式良好的数据，你可以用代码检查。例如，你可以要求智能体将任务分类为几个类别，然后根据类别选择下一个智能体）
-   Chaining multiple agents by transforming the output of one into the input of the next. You can decompose a task like writing a blog post into a series of steps - do research, write an outline, write the blog post, critique it, and then improve it.
（- 通过将一个智能体的输出转换为下一个智能体的输入来链接多个智能体。你可以将写博客文章这样的任务分解为一系列步骤 - 做研究、写大纲、写博客文章、批评它，然后改进它）
-   Running the agent that performs the task in a `while` loop with an agent that evaluates and provides feedback, until the evaluator says the output passes certain criteria.
（- 在`while`循环中运行执行任务的智能体和一个评估并提供反馈的智能体，直到评估者说输出符合某些标准）
-   Running multiple agents in parallel, e.g. via Python primitives like `asyncio.gather`. This is useful for speed when you have multiple tasks that don't depend on each other.
（- 并行运行多个智能体，例如通过Python原语如`asyncio.gather`。当你有多个不相互依赖的任务时，这对速度很有用）

We have a number of examples in [`examples/agent_patterns`](https://github.com/openai/openai-agents-python/tree/main/examples/agent_patterns).
（我们在[`examples/agent_patterns`](https://github.com/openai/openai-agents-python/tree/main/examples/agent_patterns)中有一些示例）
