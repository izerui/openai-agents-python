# 配置SDK

## API密钥和客户端

默认情况下，SDK在导入时会查找`OPENAI_API_KEY`环境变量用于LLM请求和追踪。如果您无法在应用程序启动前设置该环境变量，可以使用[set_default_openai_key()][agents.set_default_openai_key]函数设置密钥。

```python
from agents import set_default_openai_key

set_default_openai_key("sk-...")
```

或者，您也可以配置要使用的OpenAI客户端。默认情况下，SDK会创建一个`AsyncOpenAI`实例，使用环境变量中的API密钥或上面设置的默认密钥。您可以使用[set_default_openai_client()][agents.set_default_openai_client]函数更改此设置。

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

custom_client = AsyncOpenAI(base_url="...", api_key="...")
set_default_openai_client(custom_client)
```

最后，您还可以自定义使用的OpenAI API。默认情况下，我们使用OpenAI Responses API。您可以通过使用[set_default_openai_api()][agents.set_default_openai_api]函数覆盖此设置以使用Chat Completions API。

```python
from agents import set_default_openai_api

set_default_openai_api("chat_completions")
```

## 追踪

追踪功能默认启用。默认情况下，它使用上一节中的OpenAI API密钥(即环境变量或您设置的默认密钥)。您可以使用[`set_tracing_export_api_key`][agents.set_tracing_export_api_key]函数专门设置用于追踪的API密钥。

```python
from agents import set_tracing_export_api_key

set_tracing_export_api_key("sk-...")
```

您也可以使用[`set_tracing_disabled()`][agents.set_tracing_disabled]函数完全禁用追踪。

```python
from agents import set_tracing_disabled

set_tracing_disabled(True)
```

## 调试日志记录

SDK有两个Python日志记录器，没有设置任何处理程序。默认情况下，这意味着警告和错误会发送到`stdout`，但其他日志会被抑制。

要启用详细日志记录，请使用[`enable_verbose_stdout_logging()`][agents.enable_verbose_stdout_logging]函数。

```python
from agents import enable_verbose_stdout_logging

enable_verbose_stdout_logging()
```

或者，您可以通过添加处理程序、过滤器、格式化程序等来自定义日志。您可以在[Python日志指南](https://docs.python.org/3/howto/logging.html)中阅读更多内容。

```python
import logging

logger = logging.getLogger("openai.agents") # or openai.agents.tracing for the Tracing logger

# To make all logs show up
logger.setLevel(logging.DEBUG)
# To make info and above show up
logger.setLevel(logging.INFO)
# To make warning and above show up
logger.setLevel(logging.WARNING)
# etc

# You can customize this as needed, but this will output to `stderr` by default
logger.addHandler(logging.StreamHandler())
```

### 日志中的敏感数据

某些日志可能包含敏感数据(例如用户数据)。如果您希望禁用这些数据的记录，请设置以下环境变量。

要禁用记录LLM输入和输出：

```bash
export OPENAI_AGENTS_DONT_LOG_MODEL_DATA=1
```

要禁用记录工具输入和输出：

```bash
export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1
