# 工具

工具让代理能够执行操作：如获取数据、运行代码、调用外部API，甚至使用计算机。Agent SDK中有三类工具：

-   Hosted tools: `托管工具`这些工具与AI模型一起运行在LLM服务器上。OpenAI提供检索、网络搜索和计算机使用作为托管工具
-   Function calling: `函数调用`允许你将任何Python函数作为工具使用
-   Agents as tools: `代理作为工具`允许你将一个代理作为工具使用，使代理能够调用其他代理而无需移交控制权

## 托管工具

使用[`OpenAIResponsesModel`]时，OpenAI提供了一些内置工具：

-   [`WebSearchTool`]允许代理进行网络搜索
-   [`FileSearchTool`]允许从OpenAI向量存储中检索信息
-   [`ComputerTool`]允许自动化计算机使用任务
-   [`CodeInterpreterTool`]允许LLM在沙盒环境中执行代码
-   [`HostedMCPTool`]向模型暴露远程MCP服务器的工具
-   [`ImageGenerationTool`]根据提示生成图像
-   [`LocalShellTool`]在你的机器上运行shell命令

```python
from agents import Agent, FileSearchTool, Runner, WebSearchTool

agent = Agent(
    name="Assistant",
    tools=[
        WebSearchTool(),
        FileSearchTool(
            max_num_results=3,
            vector_store_ids=["VECTOR_STORE_ID"],
        ),
    ],
)

async def main():
    result = await Runner.run(agent, "Which coffee shop should I go to, taking into account my preferences and the weather today in SF?")
    print(result.final_output)
```

## 函数工具

你可以将任何Python函数作为工具使用。Agents SDK会自动设置工具：

-   工具名称将是Python函数的名称（或者你可以提供名称）
-   工具描述将从函数的docstring中获取（或者你可以提供描述）
-   函数输入的schema将从函数参数自动创建
-   每个输入的描述将从函数的docstring中获取，除非禁用

我们使用Python的`inspect`模块提取函数签名，使用[`griffe`]解析docstring，使用`pydantic`创建schema

```python
import json

from typing_extensions import TypedDict, Any

from agents import Agent, FunctionTool, RunContextWrapper, function_tool


class Location(TypedDict):
    lat: float
    long: float

@function_tool  # (1)!
async def fetch_weather(location: Location) -> str:
    # (2)!
    """Fetch the weather for a given location.

    Args:
        location: The location to fetch the weather for.
    """
    # In real life, we'd fetch the weather from a weather API
    # 实际应用中，我们会从天气API获取天气
    return "sunny"


@function_tool(name_override="fetch_data")  # (3)!
def read_file(ctx: RunContextWrapper[Any], path: str, directory: str | None = None) -> str:
    """Read the contents of a file.

    Args:
        path: The path to the file to read.
        directory: The directory to read the file from.
    """
    # In real life, we'd read the file from the file system
    # 实际应用中，我们会从文件系统读取文件
    return "<file contents>"


agent = Agent(
    name="Assistant",
    tools=[fetch_weather, read_file],  # (4)!
)

for tool in agent.tools:
    if isinstance(tool, FunctionTool):
        print(tool.name)
        print(tool.description)
        print(json.dumps(tool.params_json_schema, indent=2))
        print()

```

1.  你可以使用任何Python类型作为函数参数，函数可以是同步或异步的
2.  如果存在docstring，将用于捕获描述和参数描述
3.  函数可以选择接受`context`（必须是第一个参数）。你也可以设置覆盖项，如工具名称、描述、使用哪种docstring风格等
4.  你可以将装饰过的函数传递给工具列表

??? 注意 "展开输出"

    ```
    fetch_weather
    Fetch the weather for a given location.
    {
    "$defs": {
      "Location": {
        "properties": {
          "lat": {
            "title": "Lat",
            "type": "number"
          },
          "long": {
            "title": "Long",
            "type": "number"
          }
        },
        "required": [
          "lat",
          "long"
        ],
        "title": "Location",
        "type": "object"
      }
    },
    "properties": {
      "location": {
        "$ref": "#/$defs/Location",
        "description": "The location to fetch the weather for."
      }
    },
    "required": [
      "location"
    ],
    "title": "fetch_weather_args",
    "type": "object"
    }

    fetch_data
    Read the contents of a file.
    {
    "properties": {
      "path": {
        "description": "The path to the file to read.",
        "title": "Path",
        "type": "string"
      },
      "directory": {
        "anyOf": [
          {
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "default": null,
        "description": "The directory to read the file from.",
        "title": "Directory"
      }
    },
    "required": [
      "path"
    ],
    "title": "fetch_data_args",
    "type": "object"
    }
    ```

### 自定义函数工具

有时，你不想使用Python函数作为工具。如果愿意，你可以直接创建[`FunctionTool`]。你需要提供：

-   `name` 名称
-   `description` 描述
-   `params_json_schema`, 即参数的JSON schema
-   `on_invoke_tool`, 这是一个异步函数，接收上下文和参数作为JSON字符串，并必须将工具输出作为字符串返回

```python
from typing import Any

from pydantic import BaseModel

from agents import RunContextWrapper, FunctionTool
```