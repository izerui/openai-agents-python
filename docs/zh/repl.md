# REPL工具

SDK提供了`run_demo_loop`用于快速交互测试。

```python
import asyncio
from agents import Agent, run_demo_loop

async def main() -> None:
    agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
    await run_demo_loop(agent)

if __name__ == "__main__":
    asyncio.run(main())
```

`run_demo_loop`会循环提示用户输入，保留对话历史。默认情况下会实时流式输出模型响应。输入`quit`或`exit`(或按`Ctrl-D`)可退出循环。
