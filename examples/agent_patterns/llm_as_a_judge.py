from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Literal

from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace

from examples.models import get_agent_chat_model

"""
本示例展示了 LLM 作为评判者的模式。
第一个 agent 生成故事大纲。
第二个 agent 评判大纲并提供反馈。
我们循环这个过程直到评判者对大纲满意为止。
"""

gpt = get_agent_chat_model('gpt')

story_outline_generator = Agent(
    name="故事大纲生成器",
    instructions=(
        "你要根据用户的输入生成一个非常简短的故事大纲。"
        "如果收到任何反馈意见，请据此改进大纲。"
        "用中文回答。"
    ),
    model=gpt,
)


story_generator = Agent(
    name="故事生成器",
    instructions=(
        "你要根据给定的大纲写一个故事。"
        "用中文回答。"
    ),
    output_type=str,
    model=gpt,
)

@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent[None](
    name="评审员",
    instructions=(
        "你要评估一个故事大纲，并判断它是否足够好。"
        "如果不够好，你需要提供反馈，说明需要改进的地方。"
        "第一次评估时，绝不要给出通过的结果。"
    ),
    output_type=EvaluationFeedback,
    model=gpt,
)


async def main() -> None:
    msg = input("你想听什么样的故事？ ")
    input_items: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    latest_outline: str | None = None

    count = 0
    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge"):
        while True:
            story_outline_result = await Runner.run(
                story_outline_generator,
                input_items,
            )

            print(f'大纲: {story_outline_result.final_output}')

            input_items = story_outline_result.to_input_list()
            latest_outline = ItemHelpers.text_message_outputs(story_outline_result.new_items)
            print("故事大纲生成完毕")

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"评审员评分: {result.score}")

            if result.score == "pass":
                print("故事大纲足够好了，退出。")
                break

            print("根据反馈重新生成大纲")

            input_items.append({"content": f"反馈: {result.feedback}", "role": "user"})
            count += 1
            if count > 5:
                print("超过最大迭代次数，退出。")
                break

    print(f"最终故事大纲: {latest_outline}")

    story_result = await Runner.run(story_generator, latest_outline)
    print('===================================')
    print(f'生成的故事: \n\n {story_result.final_output}')


if __name__ == "__main__":
    asyncio.run(main())
