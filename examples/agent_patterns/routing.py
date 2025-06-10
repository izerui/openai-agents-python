import asyncio
import uuid

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace

from examples.models import get_agent_chat_model

"""
本示例展示了任务移交/路由模式。分诊 agent 接收第一条消息，然后
根据请求的语言将任务移交给相应的 agent。响应会以流式方式返回给用户。
"""

deepseek = get_agent_chat_model('deepseek-v3')

french_agent = Agent(
    name="法语助手",
    instructions="你只说法语",
    model=deepseek,
)

spanish_agent = Agent(
    name="西班牙语助手",
    instructions="你只说西班牙语",
    model=deepseek,
)

english_agent = Agent(
    name="英语助手",
    instructions="你只说英语",
    model=deepseek,
)

triage_agent = Agent(
    name="分诊助手",
    instructions="根据请求的语言将任务移交给相应的助手，不要直接回答。",
    handoffs=[french_agent, spanish_agent, english_agent],
    model=deepseek,
)


async def main():
    # We'll create an ID for this conversation, so we can link each trace
    conversation_id = str(uuid.uuid4().hex[:16])

    msg = input("嗨！我们会说法语、西班牙语和英语。有什么我可以帮忙的吗？ ")
    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        # 每个对话轮次都是一个独立的 trace。通常情况下，用户的每个输入都会是一个
        # 发送到你的应用的 API 请求，你可以用 trace() 包装这个请求
        with trace("路由示例", group_id=conversation_id):
            result = Runner.run_streamed(
                agent,
                input=inputs,
            )
            async for event in result.stream_events():
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    print(data.delta, end="", flush=True)
                elif isinstance(data, ResponseContentPartDoneEvent):
                    print("\n")

        inputs = result.to_input_list()
        print("\n")

        user_msg = input("输入消息： ")
        inputs.append({"content": user_msg, "role": "user"})
        agent = result.current_agent
        print(f'交接: {agent.name}\n')


if __name__ == "__main__":
    asyncio.run(main())

# === 音频相关事件 ===
# ResponseAudioDeltaEvent:         音频增量事件 - 流式返回音频数据片段
# ResponseAudioDoneEvent:          音频完成事件 - 音频生成完成
# ResponseAudioTranscriptDeltaEvent:   音频转写增量事件 - 流式返回语音识别文本
# ResponseAudioTranscriptDoneEvent:    音频转写完成事件 - 语音识别完成

# === 代码解释器相关事件 ===
# ResponseCodeInterpreterCallCodeDeltaEvent:   代码解释器代码增量事件 - 代码生成过程
# ResponseCodeInterpreterCallCodeDoneEvent:    代码解释器代码完成事件 - 代码生成完成
# ResponseCodeInterpreterCallCompletedEvent:   代码解释器调用完成事件
# ResponseCodeInterpreterCallInProgressEvent:  代码解释器调用进行中事件
# ResponseCodeInterpreterCallInterpretingEvent:代码解释器解释中事件

# === 基本响应事件 ===
# ResponseCompletedEvent:           响应完成事件
# ResponseContentPartAddedEvent:    内容部分添加事件
# ResponseContentPartDoneEvent:     内容部分完成事件
# ResponseCreatedEvent:             响应创建事件
# ResponseErrorEvent:               错误事件
# ResponseFailedEvent:              失败事件
# ResponseIncompleteEvent:          未完成事件
# ResponseInProgressEvent:          进行中事件
# ResponseQueuedEvent:              排队中事件

# === 文件搜索相关事件 ===
# ResponseFileSearchCallCompletedEvent:   文件搜索调用完成事件
# ResponseFileSearchCallInProgressEvent:  文件搜索调用进行中事件
# ResponseFileSearchCallSearchingEvent:   文件搜索调用搜索中事件

# === 函数调用相关事件 ===
# ResponseFunctionCallArgumentsDeltaEvent:    函数调用参数增量事件
# ResponseFunctionCallArgumentsDoneEvent:     函数调用参数完成事件

# === 输出项相关事件 ===
# ResponseOutputItemAddedEvent:           输出项添加事件
# ResponseOutputItemDoneEvent:            输出项完成事件
# ResponseOutputTextAnnotationAddedEvent: 输出文本注释添加事件

# === 推理相关事件 ===
# ResponseReasoningDeltaEvent:                推理增量事件
# ResponseReasoningDoneEvent:                 推理完成事件
# ResponseReasoningSummaryDeltaEvent:         推理摘要增量事件
# ResponseReasoningSummaryDoneEvent:          推理摘要完成事件
# ResponseReasoningSummaryPartAddedEvent:     推理摘要部分添加事件
# ResponseReasoningSummaryPartDoneEvent:      推理摘要部分完成事件
# ResponseReasoningSummaryTextDeltaEvent:     推理摘要文本增量事件
# ResponseReasoningSummaryTextDoneEvent:      推理摘要文本完成事件

# === 拒绝响应相关事件 ===
# ResponseRefusalDeltaEvent:      拒绝响应增量事件
# ResponseRefusalDoneEvent:       拒绝响应完成事件

# === 文本相关事件 ===
# ResponseTextDeltaEvent:         文本增量事件
# ResponseTextDoneEvent:          文本完成事件

# === 网络搜索相关事件 ===
# ResponseWebSearchCallCompletedEvent:    网络搜索调用完成事件
# ResponseWebSearchCallInProgressEvent:   网络搜索调用进行中事件
# ResponseWebSearchCallSearchingEvent:    网络搜索调用搜索中事件

# === 图像生成相关事件 ===
# ResponseImageGenCallCompletedEvent:     图像生成调用完成事件
# ResponseImageGenCallGeneratingEvent:    图像生成调用生成中事件
# ResponseImageGenCallInProgressEvent:    图像生成调用进行中事件
# ResponseImageGenCallPartialImageEvent:  图像生成调用部分图像事件

# === MCP(模型控制面板)相关事件 ===
# ResponseMcpCallArgumentsDeltaEvent:     MCP调用参数增量事件
# ResponseMcpCallArgumentsDoneEvent:      MCP调用参数完成事件
# ResponseMcpCallCompletedEvent:          MCP调用完成事件
# ResponseMcpCallFailedEvent:             MCP调用失败事件
# ResponseMcpCallInProgressEvent:         MCP调用进行中事件
# ResponseMcpListToolsCompletedEvent:     MCP工具列表完成事件
# ResponseMcpListToolsFailedEvent:        MCP工具列表失败事件
# ResponseMcpListToolsInProgressEvent:    MCP工具列表进行中事件