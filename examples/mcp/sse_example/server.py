import random

import requests
from mcp.server.fastmcp import FastMCP

# 创建SSE服务器实例
mcp = FastMCP("回声服务器")


@mcp.tool()
def add(a: int, b: int) -> int:
    """两个数字相加"""
    print(f"[调试-服务器] add({a}, {b})")
    return a + b


@mcp.tool()
def get_secret_word() -> str:
    """获取随机秘密单词"""
    print("[调试-服务器] get_secret_word()")
    return random.choice(["苹果", "香蕉", "樱桃"])


@mcp.tool()
def get_current_weather(city: str) -> str:
    """获取指定城市的当前天气"""
    print(f"[调试-服务器] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}?format=3")  # 使用简洁格式
    return response.text


if __name__ == "__main__":
    # 启动SSE服务器
    mcp.run(transport="sse")
