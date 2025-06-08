# 上下文管理

Context `上下文`是一个重载的术语。您可能关心的主要有两类上下文：

1. 本地代码可用的上下文：这是在工具函数运行时、在`on_handoff`等回调期间、在生命周期钩子中您可能需要的数据和依赖项。
2. 大语言模型可用的上下文：这是大语言模型在生成响应时看到的数据。

## 本地上下文

这是通过[`RunContextWrapper`][agents.run_context.RunContextWrapper]类和其中的[`context`][agents.run_context.RunContextWrapper.context]属性表示的。其工作方式是：

1. 您可以创建任何想要的Python对象。常见模式是使用数据类或Pydantic对象。
2. 您将该对象传递给各种运行方法(例如`Runner.run(..., **context=whatever**))`。
3. 您的所有工具调用、生命周期钩子等都将被传递一个包装器对象`RunContextWrapper[T]`，其中`T`表示您可以通过`wrapper.context`访问的上下文对象类型。

**最重要**的是要注意：给定智能体运行的每个智能体、工具函数、生命周期等必须使用相同类型的上下文。

您可以将上下文用于以下用途：

-   运行的上下文数据(例如用户名/uid或其他用户信息)
-   依赖项(例如日志记录器对象、数据获取器等)
-   辅助函数

!!! 重要 "信息"

    上下文对象**不会**发送给大语言模型。它纯粹是一个本地对象，您可以从中读取、写入和调用方法。

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

1. 这是上下文对象。我们在这里使用了数据类，但您可以使用任何类型。
2. 这是一个工具。您可以看到它接收一个`RunContextWrapper[UserInfo]`。工具实现从上下文中读取。
3. 我们用泛型`UserInfo`标记智能体，以便类型检查器可以捕获错误(例如，如果我们尝试传递一个接收不同上下文类型的工具)。
4. 上下文被传递给`run`函数。
5. 智能体正确调用工具并获取年龄。

## 智能体/大语言模型上下文

当调用大语言模型时，它**唯一**能看到的数据来自对话历史记录。这意味着如果您想使某些新数据对大语言模型可用，您必须以使其在该历史记录中可用的方式来实现。有几种方法可以做到这一点：

1. 您可以将其添加到智能体`instructions`中。这也称为"系统提示"或"开发者消息"。系统提示可以是静态字符串，也可以是接收上下文并输出字符串的动态函数。这是对于始终有用的信息(例如用户名或当前日期)的常见策略。
2. 在调用`Runner.run`函数时将其添加到`input`中。这与`instructions`策略类似，但允许您拥有在[命令链](https://cdn.openai.com/spec/model-spec-2024-05-08.html#follow-the-chain-of-command)中较低级别的消息。
3. 通过函数工具公开它。这对于_按需_上下文很有用 - 大语言模型决定何时需要某些数据，并可以调用工具来获取该数据。
4. 使用检索或网络搜索。这些是能够从文件或数据库(检索)或从网络(网络搜索)获取相关数据的特殊工具。这对于将响应"基于"相关上下文数据很有用。
