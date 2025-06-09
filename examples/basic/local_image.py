import asyncio
import base64
import os

from agents import Agent, Runner

from examples.models import set_global_model

set_global_model('gpt')

FILEPATH = os.path.join(os.path.dirname(__file__), "media/image_bison.jpg")


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


async def main():
    # Print base64-encoded image
    b64_image = image_to_base64(FILEPATH)

    agent = Agent(
        name="Assistant",
        instructions="你是一个有用的助手，你可以回答有关图像的问题。",
    )

    result = await Runner.run(
        agent,
        [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "detail": "auto",
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    }
                ],
            },
            {
                "role": "user",
                "content": "这张图你怎么看？",
            },
        ],
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
