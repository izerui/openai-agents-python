import asyncio
import shutil

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStdio

from examples.models import get_agent_chat_model


async def run(mcp_server: MCPServer):
    deepseek = get_agent_chat_model("deepseek-v3")
    agent = Agent(
        name="Assistant",
        instructions="使用 MCP 来操作浏览器进行网页操作。",
        mcp_servers=[mcp_server],
        model=deepseek,
    )

    # List the files it can read
    message = "智能体 mcp client 跟 mcp server 通过什么方式建立沟通 mcp 几种方式？"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask about books
    message = "访问下youtube，看看我最喜欢的歌曲列表。"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    # Ask a question that reads then reasons.
    message = "从sina中获取最新的新闻标题，并告诉我有哪些？"
    print(f"\n\nRunning: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerStdio(
            name="控制浏览器进行相关操作",
            params={
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
            },
    ) as server:
        await run(server)


if __name__ == "__main__":
    # Let's make sure the user has npx installed
    if not shutil.which("npx"):
        raise RuntimeError("npx is not installed. Please install it with `npm install -g npx`.")

    asyncio.run(main())
