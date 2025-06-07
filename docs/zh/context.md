# 上下文管理

"上下文"(Context)是一个多义词。在开发中主要涉及两类上下文：

1. 本地代码可用的上下文：指工具函数运行时、`on_handoff`等回调中或生命周期钩子中可能需要的数据和依赖项
2. LLM可用的上下文：指LLM生成响应时能看到的数据

## 本地上下文

通过[`RunContextWrapper`][agents.run_context.RunContextWrapper]类和其中的[`context`][agents.run_context.RunContextWrapper.context]属性实现。工作机制如下：

1. 创建任意Python对象，常用模式是使用dataclass或Pydantic对象
2. 将该对象传递给各种运行方法（例如`Runner.run(..., **context=whatever**)`）
3. 所有工具调用、生命周期钩子等都会收到一个包装器对象`RunContextWrapper[T]`，其中`T`表示您可以通过`wrapper.context`访问的上下文对象类型

**最重要**的一点是：给定代理运行中的每个代理、工具函数、生命周期等必须使用相同_类型_的上下文。

上下文可用于以下场景：

-   运行时的上下文数据（例如用户名/用户ID或其他用户信息）
-   依赖项（例如日志记录器对象、数据获取器等）
-   辅助函数

!!! danger "注意"

    上下文对象**不会**发送给LLM。它只是一个本地对象，您可以读取、写入并调用其方法。

```python
import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool

@dataclass
class UserInfo:  # (1)!
    name: str
    uid: int

@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:  # (2)!
    return f"User {wrapper.context.name} is 47 years old"

async def main():
    user_info = UserInfo(name="John", uid=123)

    agent = Agent[UserInfo](  # (3)!
        name="Assistant",
        tools=[fetch_user_age],
    )

    result = await Runner.run(  # (4)!
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
    )

    print(result.final_output)  # (5)!
    # The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())
```

1. 这是上下文对象。我们在此使用了dataclass，但您可以使用任何类型
2. 这是一个工具函数。可以看到它接收`RunContextWrapper[UserInfo]`参数，工具实现从上下文中读取数据
3. 我们用泛型`UserInfo`标记代理，以便类型检查器能捕获错误（例如，如果我们尝试传递使用不同上下文类型的工具）
4. 上下文被传递给`run`函数
5. 代理正确调用工具并获取年龄信息

## Agent/LLM上下文

当调用LLM时，它**唯一**能看到的数据来自对话历史。这意味着如果您想让LLM获取新数据，必须通过某种方式将其加入对话历史。有几种实现方法：

1. 可以将其添加到Agent的`instructions`中。这也被称为"系统提示"或"开发者消息"。系统提示可以是静态字符串，也可以是接收上下文并输出字符串的动态函数。这是处理总是有用的信息（例如用户名或当前日期）的常用策略
2. 在调用`Runner.run`函数时将其添加到`input`中。这与`instructions`策略类似，但允许您在[命令链](https://cdn.openai.com/spec/model-spec-2024-05-08.html#follow-the-chain-of-command)中放置较低优先级的消息
3. 通过函数工具公开它。这对_按需_上下文很有用 - LLM决定何时需要某些数据，并可以调用工具来获取该数据
4. 使用检索或网络搜索。这些是特殊工具，能够从文件或数据库（检索）或从网络（网络搜索）获取相关数据。这对于将响应"锚定"在相关上下文数据中很有用
