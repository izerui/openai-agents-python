import asyncio
import random
from typing import Literal

from agents import Agent, RunContextWrapper, Runner

from examples.models import get_agent_chat_model


class CustomContext:
    def __init__(self, style: Literal["haiku", "pirate", "robot"]):
        self.style = style


def custom_instructions(
    run_context: RunContextWrapper[CustomContext], agent: Agent[CustomContext]
) -> str:
    context = run_context.context
    if context.style == "haiku":
        return "以haikus的形式回应，使用简短的三行诗句。"
    elif context.style == "pirate":
        return "以海盗的身份回应，使用海盗的语气和表情符号。"
    else:
        return "以机器人身份回应，使用机器人的语气和表情符号。"

deepseekv3 = get_agent_chat_model('deepseek-v3')

agent = Agent(
    name="Chat agent",
    instructions=custom_instructions,
    model=deepseekv3,
)


async def main():
    choice: Literal["haiku", "pirate", "robot"] = random.choice(["haiku", "pirate", "robot"])
    context = CustomContext(style=choice)
    print(f"Using style: {choice}\n")

    user_message = "给我讲个笑话."
    print(f"User: {user_message}")
    result = await Runner.run(agent, user_message, context=context)

    print(f"Assistant: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())

"""
$ python examples/basic/dynamic_system_prompt.py
使用风格：俳句

用户：给我讲个笑话。
助手：为何鸡蛋不说笑？
恐怕会打破外壳，
蛋黄满脸。

$ python examples/basic/dynamic_system_prompt.py
使用风格：机器人

用户：给我讲个笑话。
助手：哔哔！为什么机器人踢足球踢得不好？哔哔...因为它总是踢出一堆 bug！哔哔！

$ python examples/basic/dynamic_system_prompt.py
使用风格：海盗

用户：给我讲个笑话。
助手：为什么海盗要去上学？

为了提高他的 arrr-文化水平！哈哈哈！ 🏴‍☠️
"""
