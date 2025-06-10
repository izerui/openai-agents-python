import asyncio

from agents import Agent, ItemHelpers, Runner, trace

from examples.models import get_agent_chat_model

"""
本示例展示了并行化模式。我们并行运行 agent 三次，然后选择最佳结果。
"""

deepseek = get_agent_chat_model('deepseek-v3')

spanish_agent = Agent(
    name="西班牙语翻译员",
    instructions="你负责将用户的消息翻译成西班牙语",
    model=deepseek,
)

translation_picker = Agent(
    name="翻译选择者",
    instructions="你需要从给定的选项中选择最佳的西班牙语翻译。",
    model=deepseek,
)


async def main():
    msg = input("你好！请输入一段文字，我们会将它翻译成西班牙语。\n\n")

    # 确保整个工作流在单个 trace 中
    with trace("并行翻译"):
        res_1, res_2, res_3 = await asyncio.gather(
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
            Runner.run(
                spanish_agent,
                msg,
            ),
        )

        outputs = [
            ItemHelpers.text_message_outputs(res_1.new_items),
            ItemHelpers.text_message_outputs(res_2.new_items),
            ItemHelpers.text_message_outputs(res_3.new_items),
        ]

        translations = "\n\n".join(outputs)
        print(f"\n\n翻译结果:\n\n{translations}")

        best_translation = await Runner.run(
            translation_picker,
            f"输入: {msg}\n\n翻译结果:\n{translations}",
        )

    print("\n\n-----")

    print(f"最佳翻译: {best_translation.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
