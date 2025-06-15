import asyncio
import shutil
import logging
from datetime import datetime

from agents import Agent, Runner, trace, ModelSettings
from agents.mcp import MCPServer, MCPServerStdio
from examples.models import get_agent_chat_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mcp_tools.log')
    ]
)
logger = logging.getLogger(__name__)


class LoggingMCPServer:
    """包装 MCP 服务器以添加日志记录"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.call_count = 0
    
    def __getattr__(self, name):
        """代理所有其他方法到原始服务器"""
        return getattr(self.server, name)
    
    async def list_tools(self):
        tools = await self.server.list_tools()
        logger.info(f"📋 获取到 {len(tools)} 个可用工具: {[tool.name for tool in tools]}")
        return tools
    
    async def call_tool(self, name: str, arguments: dict):
        self.call_count += 1
        call_id = f"CALL-{self.call_count:03d}"
        
        logger.info(f"🔧 [{call_id}] 开始调用工具: {name}")
        logger.info(f"📥 [{call_id}] 工具参数: {arguments}")
        
        start_time = datetime.now()
        
        try:
            result = await self.server.call_tool(name, arguments)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 截断结果以便日志显示
            result_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            
            logger.info(f"✅ [{call_id}] 工具调用成功 (耗时: {duration:.2f}s)")
            logger.info(f"📤 [{call_id}] 返回结果预览: {result_preview}")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"❌ [{call_id}] 工具调用失败 (耗时: {duration:.2f}s): {str(e)}")
            raise


async def run(mcp_server: MCPServer):
    logger.info("🚀 开始运行 MCP Fetch 示例")
    
    # 包装服务器以添加日志记录
    logging_server = LoggingMCPServer(mcp_server)
    
    deepseek = get_agent_chat_model('deepseek-v3')
    
    logger.info("🤖 创建 Agent")
    agent = Agent(
        name="Assistant",
        instructions="""
        你是一个网页内容获取助手。
        """,
        mcp_servers=[logging_server],  # 使用包装后的服务器
        # model_settings=ModelSettings(tool_choice="required"),
        model=deepseek,
    )

    message = "请获取 https://www.cherry-ai.com/ 的html网页内容，并列出这个软件支持的主要功能介绍。"
    
    logger.info(f"💬 用户消息: {message}")

    # 添加自定义的运行监控
    logger.info("▶️  开始 Agent 运行")
    result = await Runner.run(starting_agent=agent, input=message)
    logger.info("⏹️  Agent 运行完成")
    
    logger.info(f"📋 最终输出: {result.final_output[:300]}{'...' if len(result.final_output) > 300 else ''}")


async def main():
    logger.info("🏁 程序开始")
    
    try:
        async with MCPServerStdio(
            name="fetch",
            cache_tools_list=True,  # Cache the tools list, for demonstration
            params={
                "command": "node",
                "args": [
                    "/Users/liuyuhua/vsprojects/fetch-mcp/dist/index.js"
                ]
            },
        ) as server:
            logger.info("🔌 MCP 服务器连接成功")
            await run(server)
            
    except Exception as e:
        logger.error(f"💥 程序运行出错: {str(e)}")
        raise
    finally:
        logger.info("🏁 程序结束")


if __name__ == "__main__":
    asyncio.run(main())
