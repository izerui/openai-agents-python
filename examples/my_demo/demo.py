import asyncio
from agents import Agent

from examples.models import set_global_model
from src.agents import run_demo_loop

set_global_model('gpt')

async def main() -> None:
    agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
    await run_demo_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())