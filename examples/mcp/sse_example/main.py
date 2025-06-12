import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings
from examples.models import get_agent_chat_model


async def run(mcp_server: MCPServer):
    """运行代理示例"""
    deepseek = get_agent_chat_model("deepseek-v3")
    agent = Agent(
        name="助手",
        instructions="使用工具回答问题",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
        model=deepseek,
    )

    # 使用`add`工具相加两个数字
    message = "计算这两个数的和：7和22"
    print(f"执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # 运行`get_weather`工具
    message = "东京的天气如何？"
    print(f"\n\n执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # 运行`get_secret_word`工具
    message = "秘密单词是什么？"
    print(f"\n\n执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    """主函数"""
    async with MCPServerSse(
        name="SSE Python服务器",
        params={
            "url": "http://localhost:8000/sse",
        },
    ) as server:
        trace_id = gen_trace_id()
        with trace(workflow_name="SSE示例", trace_id=trace_id):
            print(f"查看追踪: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
            await run(server)


if __name__ == "__main__":
    # 检查用户是否安装了uv
    if not shutil.which("uv"):
        raise RuntimeError(
            "未安装uv。请安装: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # 在子进程中运行SSE服务器。通常这会是一个远程服务器，
    # 但在这个演示中，我们将在本地运行它：http://localhost:8000/sse
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")

        print("正在启动SSE服务器: http://localhost:8000/sse ...")

        # 运行`uv run server.py`启动SSE服务器
        process = subprocess.Popen(["uv", "run", server_file])
        # 等待3秒让它启动
        time.sleep(3)

        print("SSE服务器已启动。正在运行示例...\n\n")
    except Exception as e:
        print(f"启动SSE服务器时出错: {e}")
        exit(1)

    try:
        asyncio.run(main())
    finally:
        if process:
            process.terminate()
