# SDK配置指南

## API密钥与客户端配置

默认情况下，SDK会在导入时自动查找`OPENAI_API_KEY`环境变量用于LLM请求和追踪。如果无法在应用启动前设置该环境变量，可以使用[set_default_openai_key()][agents.set_default_openai_key]函数设置密钥。

```python
from agents import set_default_openai_key

set_default_openai_key("sk-...")
```

此外，您也可以配置自定义的OpenAI客户端。默认情况下，SDK会创建一个`AsyncOpenAI`实例，使用环境变量或上述设置的默认密钥。您可以通过[set_default_openai_client()][agents.set_default_openai_client]函数修改此行为。

```python
from openai import AsyncOpenAI
from agents import set_default_openai_client

custom_client = AsyncOpenAI(base_url="...", api_key="...")
set_default_openai_client(custom_client)
```

最后，您还可以自定义使用的OpenAI API。默认情况下，我们使用OpenAI Responses API。您可以通过[set_default_openai_api()][agents.set_default_openai_api]函数切换为Chat Completions API。

```python
from agents import set_default_openai_api

set_default_openai_api("chat_completions")
```

## 追踪功能

追踪功能默认启用。默认使用上述章节中的OpenAI API密钥（即环境变量或您设置的默认密钥）。您可以使用[`set_tracing_export_api_key`][agents.set_tracing_export_api_key]函数专门设置用于追踪的API密钥。

```python
from agents import set_tracing_export_api_key

set_tracing_export_api_key("sk-...")
```

您也可以通过[`set_tracing_disabled()`][agents.set_tracing_disabled]函数完全禁用追踪功能。

```python
from agents import set_tracing_disabled

set_tracing_disabled(True)
```

## 调试日志

SDK内置两个未设置处理器的Python日志记录器。默认情况下，这意味着警告和错误会输出到`stdout`，而其他日志会被抑制。

要启用详细日志输出，请使用[`enable_verbose_stdout_logging()`][agents.enable_verbose_stdout_logging]函数。

```python
from agents import enable_verbose_stdout_logging

enable_verbose_stdout_logging()
```

或者，您也可以通过添加处理器、过滤器、格式化程序等自定义日志。更多信息请参阅[Python日志指南](https://docs.python.org/3/howto/logging.html)。

```python
import logging

logger = logging.getLogger("openai.agents") # 或openai.agents.tracing获取追踪日志记录器

# 显示所有日志
logger.setLevel(logging.DEBUG)
# 显示info及以上级别日志
logger.setLevel(logging.INFO)
# 显示warning及以上级别日志
logger.setLevel(logging.WARNING)
# 等等

# 您可以根据需要自定义，默认会输出到`stderr`
logger.addHandler(logging.StreamHandler())
```

### 日志中的敏感数据

某些日志可能包含敏感数据（例如用户数据）。如果您希望禁止记录这些数据，请设置以下环境变量。

禁止记录LLM输入输出：

```bash
export OPENAI_AGENTS_DONT_LOG_MODEL_DATA=1
```

禁止记录工具输入输出：

```bash
export OPENAI_AGENTS_DONT_LOG_TOOL_DATA=1
