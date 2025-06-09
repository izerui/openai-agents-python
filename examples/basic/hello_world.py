import asyncio

from agents import Agent, Runner
from agents import RunConfig

from examples.models import get_runner_model_provider


async def main():
    deepseekv3_provider = get_runner_model_provider('deepseek-v3')

    agent = Agent(
        name="Assistant",
        instructions="使用简短的语句回复",
    )

    result = await Runner.run(agent,
                              "告诉我有关编程递归的信息.",
                              run_config=RunConfig(model_provider=deepseekv3_provider), )
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())
