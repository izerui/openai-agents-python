# 代理可视化

代理可视化允许您使用**Graphviz**生成代理及其关系的结构化图形表示。这对于理解代理、工具和交接在应用程序中如何交互非常有用。

## 安装

安装可选的`viz`依赖组：

```bash
pip install "openai-agents[viz]"
```

## 生成图表

您可以使用`draw_graph`函数生成代理可视化。该函数创建一个有向图，其中：

- **代理**显示为黄色方框。
- **工具**显示为绿色椭圆。
- **交接**是从一个代理指向另一个代理的有向边。

### 示例用法

```python
from agents import Agent, function_tool
from agents.extensions.visualization import draw_graph

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
    tools=[get_weather],
)

draw_graph(triage_agent)
```

![Agent Graph](../assets/images/graph.png)

这将生成一个图表，直观地表示**分诊代理**的结构及其与子代理和工具的连接。

## 理解可视化

生成的图表包括：

- **开始节点**(`__start__`)表示入口点。
- 代理显示为黄色填充的**矩形**。
- 工具显示为绿色填充的**椭圆**。
- 表示交互的有向边：
  - **实线箭头**表示代理间的交接。
  - **虚线箭头**表示工具调用。
- **结束节点**(`__end__`)表示执行终止的位置。

## 自定义图表

### 显示图表
默认情况下，`draw_graph`会内联显示图表。要在单独窗口中显示图表，请编写以下代码：

```python
draw_graph(triage_agent).view()
```

### 保存图表
默认情况下，`draw_graph`会内联显示图表。要将其保存为文件，请指定文件名：

```python
draw_graph(triage_agent, filename="agent_graph")
```

这将在工作目录中生成`agent_graph.png`。
