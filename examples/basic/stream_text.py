import asyncio

from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, Runner

from examples.models import get_agent_chat_model

deepseekv3 = get_agent_chat_model('deepseek-v3')

async def main():
    agent = Agent(
        name="Joker",
        instructions="您是一个有益的助手。",
        model=deepseekv3
    )

    result = Runner.run_streamed(agent, input="请告诉我5个笑话。")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
