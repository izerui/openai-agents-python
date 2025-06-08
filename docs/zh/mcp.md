# MCP模型上下文协议

[模型上下文协议](https://modelcontextprotocol.io/introduction)(简称MCP)是为LLM提供工具和上下文的一种方式。根据MCP文档:

> MCP是一个开放协议，标准化了应用程序如何向LLM提供上下文。可以把MCP想象成AI应用的USB-C接口。就像USB-C为设备连接各种外设和配件提供了标准化方式，MCP为AI模型连接不同数据源和工具提供了标准化方式。

Agents SDK支持MCP。这使您能够使用各种MCP服务器为您的Agent提供工具。

## MCP服务器

目前，MCP规范根据传输机制定义了三种服务器:

1. **stdio** 服务器作为应用程序的子进程运行。可以认为它们在"本地"运行。
2. **HTTP over SSE** 服务器远程运行。通过URL连接它们。
3. **Streamable HTTP** 服务器使用MCP规范中定义的Streamable HTTP传输远程运行。

您可以使用[`MCPServerStdio`][agents.mcp.server.MCPServerStdio], [`MCPServerSse`][agents.mcp.server.MCPServerSse]和[`MCPServerStreamableHttp`][agents.mcp.server.MCPServerStreamableHttp]类来连接这些服务器。

例如，这是使用[官方MCP文件系统服务器](https://www.npmjs.com/package/@modelcontextprotocol/server-filesystem)的方式。

```python
async with MCPServerStdio(
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
    }
) as server:
    tools = await server.list_tools()
```

## 使用MCP服务器

MCP服务器可以添加到Agent中。每次运行Agent时，Agents SDK都会在MCP服务器上调用`list_tools()`。这使得LLM能够了解MCP服务器的工具。当LLM调用MCP服务器的工具时，SDK会在该服务器上调用`call_tool()`。

```python

agent=Agent(
    name="Assistant",
    instructions="Use the tools to achieve the task",
    mcp_servers=[mcp_server_1, mcp_server_2]
)
```

## 缓存

每次Agent运行时，它都会在MCP服务器上调用`list_tools()`。这可能会造成延迟，特别是如果服务器是远程服务器。要自动缓存工具列表，可以将`cache_tools_list=True`传递给[`MCPServerStdio`][agents.mcp.server.MCPServerStdio], [`MCPServerSse`][agents.mcp.server.MCPServerSse]和[`MCPServerStreamableHttp`][agents.mcp.server.MCPServerStreamableHttp]。只有在确定工具列表不会更改时才应这样做。

如果要使缓存失效，可以在服务器上调用`invalidate_tools_cache()`。

## 端到端示例

查看完整的运行示例在[examples/mcp](https://github.com/openai/openai-agents-python/tree/main/examples/mcp)。

## 追踪

[追踪](./tracing.md)自动捕获MCP操作，包括:

1. 调用MCP服务器列出工具
2. 函数调用中与MCP相关的信息

![MCP Tracing Screenshot](../assets/images/mcp-tracing.jpg)
