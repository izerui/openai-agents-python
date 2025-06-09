import asyncio
import random

import requests
from agents import Agent, ItemHelpers, Runner, function_tool
from openai.types.responses import ResponseTextDeltaEvent

from examples.basic.lifecycle_example import deepseekv3
from examples.models import get_agent_chat_model


@function_tool
def fetch_url(url:str) -> str:
    """
    Fetches the content from the specified URL.

    This function takes a URL as input and retrieves its content.
    The content fetched from the URL is returned as a string.
    This is a synchronous function and may block until the request is completed.

    Parameters:
        url: str
            The URL from which to fetch content.

    Returns:
        str
            The content retrieved from the specified URL.
    """
    response = requests.get(url)
    # 尝试自动检测编码
    response.encoding = response.apparent_encoding
    return response.text

qwen_max = get_agent_chat_model('qwen-max')

async def main():
    agent = Agent(
        name="Joker",
        instructions="你是一个有用的助手，可以抓取网页内容并回答有关网页内容的问题。",
        tools=[fetch_url],
        model=qwen_max,
    )

    result = Runner.run_streamed(
        agent,
        input="""
        分别爬取deepseek的定价页面和qwen的定价页面，分析并总结下价格优势对比。
        deepseek: https://api-docs.deepseek.com/zh-cn/quick_start/pricing
        qwen: https://finance.sina.com.cn/tech/digi/2024-12-31/doc-inecitzz2090973.shtml
        """,
    )
    print("=== Run starting ===")
    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            if isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
            continue
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                # 这里我们可以输出最终的全部消息内容
                # print("最终输出:")
                # print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                pass
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())

    # === Run starting ===
    # Agent updated: Joker
    # -- Tool was called
    # -- Tool output: 4
    # -- Message output:
    #  Sure, here are four jokes for you:

    # 1. **Why don't skeletons fight each other?**
    #    They don't have the guts!

    # 2. **What do you call fake spaghetti?**
    #    An impasta!

    # 3. **Why did the scarecrow win an award?**
    #    Because he was outstanding in his field!

    # 4. **Why did the bicycle fall over?**
    #    Because it was two-tired!
    # === Run complete ===
