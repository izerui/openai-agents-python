import asyncio
import os
import shutil

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStdio
from agents.model_settings import ModelSettings

from examples.models import get_agent_chat_model


async def run(mcp_server: MCPServer):
    deepseek = get_agent_chat_model("deepseek-v3")
    agent = Agent(
        name="Assistant",
        instructions="""你是一个文件系统助手。你必须使用提供的工具来读取和分析文件系统中的文件。
重要：每次回答问题时，都必须首先使用工具来读取相关文件，然后基于文件内容给出答案。
绝对不要凭空猜测文件内容，必须实际读取文件。

可用的工具包括：
- read_file: 读取文件内容
- list_directory: 列出目录内容
- 其他文件系统操作工具

请务必使用这些工具来获取实际的文件信息。""",
        mcp_servers=[mcp_server],
        model=deepseek,
        model_settings=ModelSettings(tool_choice="required")  # 强制使用工具
    )

    # 首先显示可用的MCP工具
    print("=== 获取MCP工具列表 ===")
    mcp_tools = await agent.get_mcp_tools()
    print(f"可用的MCP工具数量: {len(mcp_tools)}")
    for tool in mcp_tools:
        print(f"- {tool.name}: {getattr(tool, 'description', 'No description')}")
    print()

    # List the files it can read
    message = "请使用工具列出当前目录下的所有文件，并读取每个文件的内容。"
    print(f"运行查询: {message}")
    print("=" * 50)
    result = await Runner.run(starting_agent=agent, input=message)
    print("Agent响应:")
    print(result.final_output)
    print("\n" + "=" * 50 + "\n")

    # Ask about books - 强制读取文件
    message = "请先读取 favorite_books.txt 文件，然后告诉我我最喜欢的书是什么（列表中的第一本）。"
    print(f"运行查询: {message}")
    print("=" * 50)
    result = await Runner.run(starting_agent=agent, input=message)
    print("Agent响应:")
    print(result.final_output)
    print("\n" + "=" * 50 + "\n")

    # Ask a question that reads then reasons.
    message = "请先读取 favorite_songs.txt 文件查看我喜欢的歌曲，然后基于这些歌曲的风格，推荐一首我可能喜欢的新歌曲。"
    print(f"运行查询: {message}")
    print("=" * 50)
    result = await Runner.run(starting_agent=agent, input=message)
    print("Agent响应:")
    print(result.final_output)
    print("\n" + "=" * 50)


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")
    
    print(f"示例文件目录: {samples_dir}")
    print(f"目录内容: {os.listdir(samples_dir)}")
    print()
    
    # 保存原始工作目录
    original_cwd = os.getcwd()
    # 切换到样本文件目录，让MCP服务器以此作为根目录
    os.chdir(samples_dir)
    
    try:
        async with MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],  # 使用当前目录
            },
        ) as server:
            print("MCP服务器已启动...")
            
            # 测试MCP服务器连接
            try:
                tools = await server.list_tools()
                print(f"MCP服务器工具数量: {len(tools)}")
                for tool in tools:
                    print(f"- MCP工具: {tool.name}")
            except Exception as e:
                print(f"获取MCP工具时出错: {e}")
                return
            
            print()
            
            trace_id = gen_trace_id()
            with trace(workflow_name="MCP Filesystem Example", trace_id=trace_id):
                print(f"查看追踪: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
                await run(server)
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())
