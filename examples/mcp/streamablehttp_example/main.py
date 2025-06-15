import asyncio
import os
import shutil
import subprocess
import time
from typing import Any

from agents import Agent, Runner, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings
from examples.models import get_agent_chat_model


async def run(mcp_server: MCPServer):

    deepseek = get_agent_chat_model("deepseek-v3")
    agent = Agent(
        name="助手",
        instructions="使用工具来回答问题。",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
        model=deepseek,
    )

    # 使用 `add` 工具来计算两个数字的和
    message = "计算这两个数字的和: 7 和 22。"
    print(f"执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"结果: {result.final_output}")

    # 运行 `get_weather` 工具
    message = "东京的天气如何?"
    print(f"\n\n执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"天气报告:\n{result.final_output}")

    # 运行 `get_secret_word` 工具
    message = "秘密单词是什么?"
    print(f"\n\n执行: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(f"秘密单词: {result.final_output}")


async def main():
    async with MCPServerStreamableHttp(
        name="可流式 HTTP Python 服务器",
        params={
            "url": "http://localhost:8000/mcp",
        },
    ) as server:
        # trace_id = gen_trace_id()
        # with trace(workflow_name="Streamable HTTP Example", trace_id=trace_id):
        #     print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}\n")
        await run(server)


if __name__ == "__main__":
    # 确保用户已安装 uv
    if not shutil.which("uv"):
        raise RuntimeError(
            "未安装 uv。请安装它: https://docs.astral.sh/uv/getting-started/installation/"
        )

    # 我们将在子进程中运行可流式 HTTP 服务器。通常这会是一个远程服务器，但在这个演示中，
    # 我们将在本地运行它: http://localhost:8000/mcp
    process: subprocess.Popen[Any] | None = None
    try:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        server_file = os.path.join(this_dir, "server.py")

        print("正在启动可流式 HTTP 服务器，地址: http://localhost:8000/mcp ...")

        # 运行 `uv run server.py` 来启动可流式 HTTP 服务器
        process = subprocess.Popen(["uv", "run", server_file])
        # 给它3秒钟启动时间
        time.sleep(3)

        print("可流式 HTTP 服务器已启动。正在运行示例...\n\n")
    except Exception as e:
        print(f"启动可流式 HTTP 服务器时出错: {e}")
        exit(1)

    asyncio.run(main())
