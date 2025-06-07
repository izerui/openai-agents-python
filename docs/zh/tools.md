# Tools (工具)

Tools let agents take actions: things like fetching data, running code, calling external APIs, and even using a computer. There are three classes of tools in the Agent SDK:
(工具让代理能够执行操作：如获取数据、运行代码、调用外部API，甚至使用计算机。Agent SDK中有三类工具：)

-   Hosted tools: these run on LLM servers alongside the AI models. OpenAI offers retrieval, web search and computer use as hosted tools.
(托管工具：这些工具与AI模型一起运行在LLM服务器上。OpenAI提供检索、网络搜索和计算机使用作为托管工具)
-   Function calling: these allow you to use any Python function as a tool.
(函数调用：允许你将任何Python函数作为工具使用)
-   Agents as tools: this allows you to use an agent as a tool, allowing Agents to call other agents without handing off to them.
(代理作为工具：允许你将一个代理作为工具使用，使代理能够调用其他代理而无需移交控制权)

## Hosted tools (托管工具)

OpenAI offers a few built-in tools when using the [`OpenAIResponsesModel`][agents.models.openai_responses.OpenAIResponsesModel]:
(使用[`OpenAIResponsesModel`]时，OpenAI提供了一些内置工具：)

-   The [`WebSearchTool`][agents.tool.WebSearchTool] lets an agent search the web.
([`WebSearchTool`]允许代理进行网络搜索)
-   The [`FileSearchTool`][agents.tool.FileSearchTool] allows retrieving information from your OpenAI Vector Stores.
([`FileSearchTool`]允许从OpenAI向量存储中检索信息)
-   The [`ComputerTool`][agents.tool.ComputerTool] allows automating computer use tasks.
([`ComputerTool`]允许自动化计算机使用任务)
-   The [`CodeInterpreterTool`][agents.tool.CodeInterpreterTool] lets the LLM execute code in a sandboxed environment.
([`CodeInterpreterTool`]允许LLM在沙盒环境中执行代码)
-   The [`HostedMCPTool`][agents.tool.HostedMCPTool] exposes a remote MCP server's tools to the model.
([`HostedMCPTool`]向模型暴露远程MCP服务器的工具)
-   The [`ImageGenerationTool`][agents.tool.ImageGenerationTool] generates images from a prompt.
([`ImageGenerationTool`]根据提示生成图像)
-   The [`LocalShellTool`][agents.tool.LocalShellTool] runs shell commands on your machine.
([`LocalShellTool`]在你的机器上运行shell命令)

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

## Function tools (函数工具)

You can use any Python function as a tool. The Agents SDK will setup the tool automatically:
(你可以将任何Python函数作为工具使用。Agents SDK会自动设置工具：)

-   The name of the tool will be the name of the Python function (or you can provide a name)
(工具名称将是Python函数的名称（或者你可以提供名称）)
-   Tool description will be taken from the docstring of the function (or you can provide a description)
(工具描述将从函数的docstring中获取（或者你可以提供描述）)
-   The schema for the function inputs is automatically created from the function's arguments
(函数输入的schema将从函数参数自动创建)
-   Descriptions for each input are taken from the docstring of the function, unless disabled
(每个输入的描述将从函数的docstring中获取，除非禁用)

We use Python's `inspect` module to extract the function signature, along with [`griffe`](https://mkdocstrings.github.io/griffe/) to parse docstrings and `pydantic` for schema creation.
(我们使用Python的`inspect`模块提取函数签名，使用[`griffe`]解析docstring，使用`pydantic`创建schema)

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

1.  You can use any Python types as arguments to your functions, and the function can be sync or async.
(你可以使用任何Python类型作为函数参数，函数可以是同步或异步的)
2.  Docstrings, if present, are used to capture descriptions and argument descriptions
(如果存在docstring，将用于捕获描述和参数描述)
3.  Functions can optionally take the `context` (must be the first argument). You can also set overrides, like the name of the tool, description, which docstring style to use, etc.
(函数可以选择接受`context`（必须是第一个参数）。你也可以设置覆盖项，如工具名称、描述、使用哪种docstring风格等)
4.  You can pass the decorated functions to the list of tools.
(你可以将装饰过的函数传递给工具列表)

??? note "Expand to see output"

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

### Custom function tools (自定义函数工具)

Sometimes, you don't want to use a Python function as a tool. You can directly create a [`FunctionTool`][agents.tool.FunctionTool] if you prefer. You'll need to provide:
(有时，你不想使用Python函数作为工具。如果愿意，你可以直接创建[`FunctionTool`]。你需要提供：)

-   `name`
(名称)
-   `description`
(描述)
-   `params_json_schema`, which is the JSON schema for the arguments
(`params_json_schema`，即参数的JSON schema)
-   `on_invoke_tool`, which is an async function that receives the context and the arguments as a JSON string, and must return the tool output as a string.
(`on_invoke_tool`，这是一个异步函数，接收上下文和参数作为JSON字符串，并必须将工具输出作为字符串返回)

```python
from typing import Any

from pydantic import BaseModel

from agents import RunContextWrapper, FunctionTool
