import argparse
import asyncio

from agents import Agent, HostedMCPTool, Runner

"""此示例演示了如何在 OpenAI Responses API 中使用托管的 MCP 支持，
而无需对任何工具进行批准。您应仅在可信的 MCP 服务器上使用此功能。"""


async def main(verbose: bool, stream: bool):
    agent = Agent(
        name="Assistant",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "gitmcp",
                    "server_url": "https://gitmcp.io/openai/codex",
                    "require_approval": "never",
                }
            )
        ],
    )

    if stream:
        result = Runner.run_streamed(agent, "这个代码库是用什么语言编写的？")
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"收到类型为 {event.item.__class__.__name__} 的事件")
        print(f"完成流式传输；最终结果: {result.final_output}")
    else:
        res = await Runner.run(agent, "这个代码库是用什么语言编写的？")
        print(res.final_output)
        # 这个代码库主要使用多种语言编写，包括 Rust 和 TypeScript...

    if verbose:
        for item in res.new_items:
            print(item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--stream", action="store_true", default=False)
    args = parser.parse_args()

    asyncio.run(main(args.verbose, args.stream))
