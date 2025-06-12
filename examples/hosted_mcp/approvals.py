import argparse
import asyncio

from agents import (
    Agent,
    HostedMCPTool,
    MCPToolApprovalFunctionResult,
    MCPToolApprovalRequest,
    Runner,
)
from dotenv import load_dotenv

"""此示例演示如何在 OpenAI Responses API 中使用托管 MCP 支持，并包含审批回调功能。"""
"""注意： 必须是 Responses API 的用户才能运行此示例。"""


def approval_callback(request: MCPToolApprovalRequest) -> MCPToolApprovalFunctionResult:
    answer = input(f"是否批准运行工具 `{request.data.name}`？(y/n) ")
    result: MCPToolApprovalFunctionResult = {"approve": answer == "y"}
    if not result["approve"]:
        result["reason"] = "用户拒绝"
    return result


load_dotenv('../openai.env', override=True)

async def main(verbose: bool, stream: bool):

    agent = Agent(
        name="Assistant",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "gitmcp",
                    "server_url": "https://gitmcp.io/openai/codex",
                    "require_approval": "always",
                },
                on_approval_request=approval_callback,
            )
        ],
    )

    if stream:
        result = Runner.run_streamed(agent, "这个代码库是用什么语言写的？")
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                print(f"收到类型为 {event.item.__class__.__name__} 的事件")
        print(f"完成流式传输；最终结果: {result.final_output}")
    else:
        res = await Runner.run(agent, "这个代码库是用什么语言写的？")
        print(res.final_output)

    if verbose:
        for item in res.new_items:
            print(item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--stream", action="store_true", default=False)
    args = parser.parse_args()

    asyncio.run(main(args.verbose, args.stream))

