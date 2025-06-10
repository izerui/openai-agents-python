import asyncio

from agents import Agent, Runner

from examples.models import set_global_model

"""本示例展示了如何使用 `previous_response_id` 参数来继续对话。
第二次运行时传入前一次响应的 ID，这样模型就可以继续对话而不需要重新发送之前的消息。

注意事项：
1. 这个功能仅适用于 OpenAI Responses API。其他模型会忽略此参数。
2. 截至目前，响应内容只会保存 30 天，所以在生产环境中你应该同时存储响应 ID
   和过期时间；如果响应已经失效，你需要重新发送之前的对话历史。
"""

set_global_model('gpt')

async def main():
    agent = Agent(
        name="助手",
        instructions="你是一个乐于助人的助手。请保持回答非常简洁。",
    )

    result = await Runner.run(agent, "南美洲最大的国家是哪个？")
    print(result.final_output)
    # 巴西

    result = await Runner.run(
        agent,
        "这个国家的首都是哪里？",
        previous_response_id=result.last_response_id,
    )
    print(result.final_output)
    # 巴西利亚


async def main_stream():
    agent = Agent(
        name="助手",
        instructions="你是一个乐于助人的助手。请保持回答非常简洁。",
    )

    result = Runner.run_streamed(agent, "南美洲最大的国家是哪个？")

    async for event in result.stream_events():
        if event.type == "raw_response_event" and event.data.type == "response.output_text.delta":
            print(event.data.delta, end="", flush=True)

    print()

    result = Runner.run_streamed(
        agent,
        "这个国家的首都是哪里？",
        previous_response_id=result.last_response_id,
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and event.data.type == "response.output_text.delta":
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    is_stream = input("是否以流模式运行？ (y/n): ")
    if is_stream == "y":
        asyncio.run(main_stream())
    else:
        asyncio.run(main())
