from __future__ import annotations as _annotations

import asyncio
import random
import uuid

from pydantic import BaseModel

from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    handoff,
    trace,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX, prompt_with_handoff_instructions

from examples.models import get_agent_chat_model


### CONTEXT


class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None


### 工具


@function_tool(
    name_override="faq_lookup_tool", description_override="查询常见问题解答。"
)
async def faq_lookup_tool(question: str) -> str:
    if "bag" in question or "baggage" in question:
        return (
            "您可以携带一个行李上飞机。"
            "行李重量必须在50磅以下，尺寸不超过22英寸 x 14英寸 x 9英寸。"
        )
    elif "seats" in question or "plane" in question:
        return (
            "飞机上共有120个座位。"
            "其中包括22个商务舱座位和98个经济舱座位。"
            "4排和16排是安全出口排。"
            "5-8排是经济舱plus，有更大的腿部空间。"
        )
    elif "wifi" in question:
        return "飞机上提供免费WiFi，请连接Airline-Wifi"
    return "抱歉，我无法回答这个问题."


@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext], confirmation_number: str, new_seat: str
) -> str:
    """
    更新指定订单号的座位信息。

    参数:
        confirmation_number: 航班订单号
        new_seat: 新的座位号
    """
    # 根据客户输入更新上下文
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    # 确保航班号已经由传入的交接设置
    assert context.context.flight_number is not None, "需要提供航班号"
    return f"已将订单 {confirmation_number} 的座位更新为 {new_seat}"


### 钩子函数


async def on_seat_booking_handoff(context: RunContextWrapper[AirlineAgentContext]) -> None:
    flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.flight_number = flight_number


### 代理

deepseekv3 = get_agent_chat_model("deepseek-v3")

faq_agent = Agent[AirlineAgentContext](
    name="常见问题代理",
    handoff_description="一个可以回答关于航空公司问题的帮助代理。",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    你是一个常见问题解答代理。如果你正在和客户交谈，你可能是由分诊代理转介过来的。
    使用以下流程来支持客户。
    # 流程
    1. 识别客户最后提出的问题。
    2. 使用常见问题查询工具来回答问题。不要依赖你自己的知识。
    3. 如果你无法回答问题，则转回给分诊代理。""",
    tools=[faq_lookup_tool],
    model=deepseekv3,
)

seat_booking_agent = Agent[AirlineAgentContext](
    name="订座代理",
    handoff_description="一个可以更新航班座位的帮助代理。",
    instructions=prompt_with_handoff_instructions(f"""
    你是一个订座代理。如果你正在和客户交谈，你可能是由分诊代理转介过来的。
    使用以下流程来支持客户。
    # 流程
    1. 询问他们的订单号。
    2. 询问客户想要的座位号。
    3. 使用更新座位工具来更新航班座位。
    如果客户询问与流程无关的问题，则转回给分诊代理。"""),
    tools=[update_seat],
    model=deepseekv3,
)

triage_agent = Agent[AirlineAgentContext](
    name="分诊代理",
    handoff_description="一个可以将客户请求分配给合适代理的分诊代理。",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "你是一个帮助分诊的代理。你可以使用你的工具将问题委派给其他合适的代理。"
    ),
    handoffs=[
        faq_agent,
        handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
    model=deepseekv3,
)

faq_agent.handoffs.append(triage_agent)
seat_booking_agent.handoffs.append(triage_agent)


### 运行


async def main():
    current_agent: Agent[AirlineAgentContext] = triage_agent
    input_items: list[TResponseInputItem] = []
    context = AirlineAgentContext()

    # 通常情况下，用户的每个输入都会是对你应用的API请求，你可以用trace()包装请求
    # 这里，我们只使用一个随机UUID作为会话ID
    conversation_id = uuid.uuid4().hex[:16]

    while True:
        user_input = input("请输入您的消息：")
        with trace("客服服务", group_id=conversation_id):
            input_items.append({"content": user_input, "role": "user"})
            result = await Runner.run(current_agent, input_items, context=context)

            for new_item in result.new_items:
                agent_name = new_item.agent.name
                if isinstance(new_item, MessageOutputItem):
                    print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
                elif isinstance(new_item, HandoffOutputItem):
                    print(
                        f"从 {new_item.source_agent.name} 转交给 {new_item.target_agent.name}"
                    )
                elif isinstance(new_item, ToolCallItem):
                    print(f"{agent_name}: 正在调用工具")
                elif isinstance(new_item, ToolCallOutputItem):
                    print(f"{agent_name}: 工具调用输出: {new_item.output}")
                else:
                    print(f"{agent_name}: 跳过项目: {new_item.__class__.__name__}")
            input_items = result.to_input_list()
            current_agent = result.last_agent


if __name__ == "__main__":
    asyncio.run(main())
