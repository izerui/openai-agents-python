import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, trace

from examples.models import get_agent_chat_model

"""
本示例演示了一个确定性流程，每一步都由一个 agent 执行。
1. 第一个 agent 生成故事大纲
2. 我们将大纲传递给第二个 agent
3. 第二个 agent 检查大纲的质量，并判断其是否为科幻故事
4. 如果大纲质量不好或不是科幻故事，则流程在此结束
5. 如果大纲质量好且是科幻故事，则将大纲传递给第三个 agent
6. 第三个 agent 根据大纲写出故事
"""

gpt = get_agent_chat_model('gpt')
deepseek = get_agent_chat_model('deepseek-v3')

story_outline_agent = Agent(
    name="story_outline_agent",
    instructions="根据用户输入生成一个非常简短的故事大纲。",
    model=deepseek,
)


class OutlineCheckerOutput(BaseModel):
    good_quality: bool
    is_scifi: bool


outline_checker_agent = Agent(
    name="outline_checker_agent",
    instructions="阅读给定的故事大纲，并判断其质量。同时判断这是否是一个科幻故事。",
    output_type=OutlineCheckerOutput,
    model=gpt,
)

story_agent = Agent(
    name="story_agent",
    instructions="根据给定的大纲写一个简短的故事。",
    output_type=str,
    model=deepseek,
)


async def main():
    input_prompt = input("你想要什么样的故事？")

    # 确保整个流程在一个 trace 中
    with trace("确定性故事流程"):
        # 1. 生成大纲
        outline_result = await Runner.run(
            story_outline_agent,
            input_prompt,
        )
        print("大纲已生成")

        # 2. 检查大纲
        outline_checker_result = await Runner.run(
            outline_checker_agent,
            outline_result.final_output,
        )

        # 3. 如果大纲质量不好或不是科幻故事，则流程在此结束
        assert isinstance(outline_checker_result.final_output, OutlineCheckerOutput)
        if not outline_checker_result.final_output.good_quality:
            print("大纲质量不好，因此流程在此结束。")
            exit(0)

        if not outline_checker_result.final_output.is_scifi:
            print("大纲不是科幻故事，因此流程在此结束。")
            exit(0)

        print("大纲质量良好且是科幻故事，因此我们继续写故事。")

        # 4. 写故事
        story_result = await Runner.run(
            story_agent,
            outline_result.final_output,
        )
        print(f"故事: {story_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
