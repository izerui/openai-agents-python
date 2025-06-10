import asyncio

from pydantic import BaseModel

from agents import Agent, Runner, function_tool

from examples.models import get_agent_chat_model


class Weather(BaseModel):
    """天气信息类"""
    city: str  # 城市名称
    temperature_range: str  # 温度范围
    conditions: str  # 天气状况


@function_tool
def get_weather(city: str) -> Weather:
    """获取指定城市的天气信息"""
    print("[调试] 正在调用天气查询")
    return Weather(city=city, temperature_range="14-20摄氏度", conditions="晴天，有风")


deepseekv3 = get_agent_chat_model('deepseek-v3')

agent = Agent(
    name="天气助手",
    instructions="你是一个乐于助人的天气助手。",
    tools=[get_weather],
    model=deepseekv3,
)


async def main():
    result = await Runner.run(agent, input="东京的天气怎么样？")
    print(result.final_output)
    # 东京今天是晴天。


if __name__ == "__main__":
    asyncio.run(main())
