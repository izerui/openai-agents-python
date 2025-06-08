# 流式处理

流式处理允许您订阅代理运行过程中的更新。这对于向最终用户显示进度更新和部分响应非常有用。

要进行流式处理，您可以调用[`Runner.run_streamed()`][agents.run.Runner.run_streamed]，它将返回一个[`RunResultStreaming`][agents.result.RunResultStreaming]。调用`result.stream_events()`会返回一个异步的[`StreamEvent`][agents.stream_events.StreamEvent]对象流，如下所述。

## 原始响应事件

[`RawResponsesStreamEvent`][agents.stream_events.RawResponsesStreamEvent]是从LLM直接传递的原始事件。它们采用OpenAI Responses API格式，意味着每个事件都有一个类型(如`response.created`、`response.output_text.delta`等)和数据。如果您想在生成后立即将响应消息流式传输给用户，这些事件非常有用。

例如，这将逐个token输出LLM生成的文本。

```python
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner

async def main():
    agent = Agent(
        name="Joker",
        instructions="You are a helpful assistant.",
    )

    result = Runner.run_streamed(agent, input="Please tell me 5 jokes.")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
```

## 运行项事件和代理事件

[`RunItemStreamEvent`][agents.stream_events.RunItemStreamEvent]是更高级别的事件。它们会在项目完全生成时通知您。这允许您在"消息生成"、"工具运行"等级别推送进度更新，而不是每个token。类似地，[`AgentUpdatedStreamEvent`][agents.stream_events.AgentUpdatedStreamEvent]在当前代理更改时(例如由于交接)提供更新。

例如，这将忽略原始事件并向用户流式传输更新。

```python
import asyncio
import random
from agents import Agent, ItemHelpers, Runner, function_tool

@function_tool
def how_many_jokes() -> int:
    return random.randint(1, 10)


async def main():
    agent = Agent(
        name="Joker",
        instructions="First call the `how_many_jokes` tool, then tell that many jokes.",
        tools=[how_many_jokes],
    )

    result = Runner.run_streamed(
        agent,
        input="Hello",
    )
    print("=== Run starting ===")

    async for event in result.stream_events():
        # We'll ignore the raw responses event deltas
        if event.type == "raw_response_event":
            continue
        # When the agent updates, print that
        elif event.type == "agent_updated_stream_event":
            print(f"Agent updated: {event.new_agent.name}")
            continue
        # When items are generated, print them
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                print("-- Tool was called")
            elif event.item.type == "tool_call_output_item":
                print(f"-- Tool output: {event.item.output}")
            elif event.item.type == "message_output_item":
                print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
            else:
                pass  # Ignore other event types

    print("=== Run complete ===")


if __name__ == "__main__":
    asyncio.run(main())
```