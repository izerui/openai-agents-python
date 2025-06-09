import asyncio

from agents import Agent, Runner

from examples.models import set_global_model

URL = "https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"

set_global_model('gpt')


async def main():
    agent = Agent(
        name="Assistant",
        instructions="你是一个有用的助手，你可以回答有关图像的问题。",
    )

    result = await Runner.run(
        agent,
        [
            {
                "role": "user",
                "content": [{"type": "input_image", "detail": "auto", "image_url": URL}],
            },
            {
                "role": "user",
                "content": "你在图像中看到了什么？",
            },
        ],
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
