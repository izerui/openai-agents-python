# MCP 文件系统示例

本示例使用[文件系统 MCP 服务器](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)，通过 `npx` 在本地运行。

运行方式：

```
uv run python examples/mcp/filesystem_example/main.py
```

## 详细说明

本示例使用来自 `agents.mcp` 的 `MCPServerStdio` 类，使用以下命令：

```bash
npx -y "@modelcontextprotocol/server-filesystem" <samples_directory>
```

它只能访问示例旁边的 `sample_files` 目录，该目录包含一些示例数据。

底层实现：

1. 服务器在子进程中启动，并提供了一系列工具，如 `list_directory()`、`read_file()` 等。
2. 我们通过 `mcp_agents` 将服务器实例添加到 Agent 中。
3. 每次 agent 运行时，我们都会通过 `server.list_tools()` 调用 MCP 服务器来获取工具列表。
4. 如果 LLM 选择使用 MCP 工具，我们会通过 `server.run_tool()` 调用 MCP 服务器来运行该工具。
