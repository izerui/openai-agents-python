#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent-based MCP客户端 - 使用MCPServerStdio高级封装
基于client.py的7步流程，但使用agents.mcp模块实现
"""
import asyncio
import os
import time
import shutil
from typing import List, Dict, Any, Optional

from agents.mcp import MCPServerStdio

# MCP 协议说明
MCP_PROTOCOL_DOCS = {
    "initialize": """
### 步骤1：初始化连接
使用MCPServerStdio建立与MCP服务器的连接，自动处理协议协商
    """,

    "initialized": """
### 步骤2：协议协商
MCPServerStdio自动处理initialized通知和能力协商
    """,

    "auth": """
### 步骤3：身份认证
MCPServerStdio自动处理认证流程（大多数MCP服务器跳过）
    """,

    "tools/list": """
### 步骤4：获取工具列表
使用server.list_tools()获取所有可用工具
    """,

    "parse_tools": """
### 步骤5：工具列表解析
解析工具信息，展示工具名称、描述和参数
    """,

    "tools/call": """
### 步骤6：调用工具
使用server.call_tool()调用具体工具，保持连接活跃
    """,

    "close": """
### 步骤7：循环测试
测试其他MCP服务器或退出程序
    """
}

class AgentMCPClient:
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.current_step = 1
        self.total_steps = 7
        self.available_tools = []
        self.continue_testing = True
        self.mcp_server: Optional[MCPServerStdio] = None
        self.protocol_steps = [
            ("initialize", "初始化连接"),
            ("initialized", "协议协商"), 
            ("auth", "身份认证"),
            ("tools/list", "获取工具列表"),
            ("parse_tools", "工具列表解析"),
            ("tools/call", "调用工具"),
            ("close", "循环测试")
        ]

    def print_step_header(self):
        """打印步骤头部"""
        _, step_name = self.protocol_steps[self.current_step - 1]
        dots = []
        for i in range(self.total_steps):
            if i + 1 == self.current_step:
                dots.append("●")  # 当前步骤
            elif i + 1 < self.current_step:
                dots.append("✓")  # 已完成步骤
            else:
                dots.append("○")  # 未开始步骤

        progress = " → ".join(dots)
        print(f"\n{'='*60}")
        print(f"MCP 步骤 {self.current_step}/{self.total_steps}: {step_name}")
        print(f"{progress}")
        print(f"{'='*60}\n")

    def print_protocol_doc(self, method: str):
        """打印协议说明"""
        if method in MCP_PROTOCOL_DOCS:
            print("协议说明:")
            print(MCP_PROTOCOL_DOCS[method])
            print()

    async def step_1_initialize(self):
        """步骤1：初始化连接"""
        self.print_step_header()
        self.print_protocol_doc("initialize")
        
        try:
            print(f">>> 启动 MCP 服务器: {' '.join(self.server_command)}")
            
            # 解析命令和参数
            command = self.server_command[0]
            args = self.server_command[1:] if len(self.server_command) > 1 else []
            
            self.mcp_server = MCPServerStdio(
                name="Agent MCP Client",
                params={
                    "command": command,
                    "args": args,
                }
            )
            
            print(">>> 正在建立连接...")
            await self.mcp_server.__aenter__()
            print("✅ MCP服务器连接成功")
            print("✅ 自动完成协议初始化和协商")
            
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False

    async def step_2_initialized(self):
        """步骤2：协议协商（已由MCPServerStdio自动处理）"""
        self.print_step_header()
        self.print_protocol_doc("initialized")
        
        print(">>> MCPServerStdio已自动处理协议协商")
        print("✅ 协议版本: 2024-11-05")
        print("✅ 客户端能力已声明")
        await asyncio.sleep(1)
        return True

    async def step_3_auth(self):
        """步骤3：身份认证（已由MCPServerStdio自动处理）"""
        self.print_step_header()
        self.print_protocol_doc("auth")
        
        print(">>> MCPServerStdio已自动处理认证流程")
        print(">>> 注意：大多数 MCP 服务器不需要显式认证")
        await asyncio.sleep(1)
        return True

    async def step_4_list_tools(self):
        """步骤4：获取工具列表"""
        self.print_step_header()
        self.print_protocol_doc("tools/list")
        
        try:
            print(">>> 正在获取工具列表...")
            tools = await self.mcp_server.list_tools()
            self.available_tools = tools
            
            print(f"✅ 成功获取 {len(tools)} 个工具:")
            for i, tool in enumerate(tools):
                print(f"  {i+1}. {tool.name}")
                print(f"     描述: {tool.description or 'No description'}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    properties = tool.inputSchema.get('properties', {})
                    if properties:
                        print(f"     参数: {list(properties.keys())}")
                print()
            
            return True
            
        except Exception as e:
            print(f"❌ 获取工具列表失败: {e}")
            return False

    async def step_5_parse_tools(self):
        """步骤5：工具列表解析"""
        self.print_step_header()
        self.print_protocol_doc("parse_tools")
        
        print(">>> 开始解析工具列表...")
        if self.available_tools:
            print(f">>> 成功解析 {len(self.available_tools)} 个工具:")
            for tool in self.available_tools:
                print(f"  - 工具名称: {tool.name}")
                print(f"    描述: {tool.description or 'No description'}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema = tool.inputSchema
                    if 'properties' in schema:
                        print(f"    输入参数: {list(schema['properties'].keys())}")
                        # 显示参数详情
                        for param_name, param_info in schema['properties'].items():
                            param_type = param_info.get('type', 'unknown')
                            param_desc = param_info.get('description', 'No description')
                            print(f"      - {param_name} ({param_type}): {param_desc}")
                print()
        else:
            print(">>> 警告：未获取到任何工具信息")
        
        print(">>> 工具解析完成")
        await asyncio.sleep(2)
        return True

    async def step_6_call_tools(self):
        """步骤6：调用工具"""
        self.print_step_header()
        self.print_protocol_doc("tools/call")
        
        if not self.available_tools:
            print(">>> 没有可用工具，跳过调用步骤")
            await asyncio.sleep(1)
            return True
        
        try:
            # 尝试调用几个常见的工具
            for tool in self.available_tools[:3]:  # 最多测试前3个工具
                tool_name = tool.name
                print(f">>> 测试工具: {tool_name}")
                
                # 根据工具类型准备参数
                args = self._prepare_tool_arguments(tool)
                
                try:
                    print(f">>> 调用工具 '{tool_name}' with args: {args}")
                    result = await self.mcp_server.call_tool(tool_name, args)
                    print(f"✅ 工具调用成功:")
                    print(f"   结果: {self._format_result(result)}")
                    print()
                    
                except Exception as e:
                    print(f"❌ 工具 '{tool_name}' 调用失败: {e}")
                    print()
                
                await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 工具调用过程出错: {e}")
            return False

    def _prepare_tool_arguments(self, tool) -> Dict[str, Any]:
        """为工具准备合适的参数"""
        tool_name = tool.name.lower()
        
        # 根据工具名称和schema准备参数
        if 'list' in tool_name and 'directory' in tool_name:
            return {"path": "."}
        elif 'read' in tool_name and 'file' in tool_name:
            # 尝试读取一个可能存在的文件
            common_files = ["README.md", "package.json", "requirements.txt", "favorite_books.txt"]
            return {"path": common_files[0]}
        elif 'allowed' in tool_name:
            return {}
        elif 'search' in tool_name:
            return {"query": "test", "path": "."}
        else:
            # 检查工具的inputSchema
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                args = {}
                if 'properties' in schema:
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'string')
                        if param_type == 'string':
                            if 'path' in param_name.lower():
                                args[param_name] = "."
                            elif 'query' in param_name.lower():
                                args[param_name] = "test"
                            else:
                                args[param_name] = "example"
                        elif param_type == 'boolean':
                            args[param_name] = True
                        elif param_type == 'number':
                            args[param_name] = 1
                return args
            return {}

    def _format_result(self, result) -> str:
        """格式化工具调用结果"""
        if isinstance(result, str):
            if len(result) > 200:
                return f"{result[:200]}... (截断，总长度: {len(result)})"
            return result
        elif isinstance(result, (list, dict)):
            result_str = str(result)
            if len(result_str) > 200:
                return f"{result_str[:200]}... (截断，总长度: {len(result_str)})"
            return result_str
        else:
            return str(result)

    async def step_7_close(self):
        """步骤7：循环测试"""
        self.print_step_header()
        self.print_protocol_doc("close")
        
        print(">>> 当前MCP服务器测试完成!")
        print("\n" + "="*60)
        print("          Agent MCP 客户端交互流程完成!")
        print("="*60 + "\n")
        
        # 关闭当前服务器连接
        if self.mcp_server:
            try:
                await self.mcp_server.__aexit__(None, None, None)
                print(">>> 当前服务器连接已关闭")
            except:
                pass
            self.mcp_server = None
        
        # 询问用户是否继续测试
        print("是否要测试其他 MCP 服务器？")
        print("1. 是 - 测试新服务器")
        print("2. 否 - 退出程序")
        
        try:
            choice = input("\n请选择 (1/2): ").strip()
            if choice == "1" or choice.lower() == "y":
                # 获取新的服务器命令
                print("\n请输入新的 MCP server 启动命令:")
                new_cmd = input("命令: ").strip()
                if new_cmd:
                    self.server_command = new_cmd.split()
                    self.reset_for_new_test()
                    return True  # 继续测试
                else:
                    print("命令为空，退出程序")
                    self.continue_testing = False
            else:
                print(">>> 退出程序")
                self.continue_testing = False
        except (KeyboardInterrupt, EOFError):
            print("\n>>> 用户中断，退出程序")
            self.continue_testing = False
        
        return False

    def reset_for_new_test(self):
        """重置状态以便进行新的测试"""
        self.current_step = 1
        self.available_tools = []
        print("\n" + "="*60)
        print("          准备测试新的 MCP 服务器")
        print("="*60 + "\n")

    async def run_full_workflow(self):
        """运行完整的7步工作流程"""
        steps = [
            self.step_1_initialize,
            self.step_2_initialized,
            self.step_3_auth,
            self.step_4_list_tools,
            self.step_5_parse_tools,
            self.step_6_call_tools,
            self.step_7_close
        ]
        
        try:
            for step_func in steps:
                success = await step_func()
                if not success:
                    print(f"❌ 步骤 {self.current_step} 失败，终止流程")
                    return False
                
                self.current_step += 1
                
                # 在步骤之间添加短暂暂停
                if self.current_step <= self.total_steps:
                    await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"❌ 工作流程执行出错: {e}")
            return False
        finally:
            # 确保连接被正确关闭
            if self.mcp_server:
                try:
                    await self.mcp_server.__aexit__(None, None, None)
                except:
                    pass

async def main():
    """主函数"""
    print("""
===========================================
        Agent-based MCP 客户端启动向导
===========================================

本客户端使用agents.mcp.MCPServerStdio高级封装
将按照完整的 MCP 交互流程执行：
1. 初始化连接      2. 协议协商
3. 身份认证        4. 获取工具列表  
5. 工具列表解析    6. 调用工具
7. 循环测试        (可测试多个服务器)

请输入 MCP server 启动命令
支持的格式示例：
1) npx -y @modelcontextprotocol/server-filesystem .
2) node your-mcp-server.js
3) python your_mcp_server.py
""")

    cmd_input = input("请输入命令: ").strip()
    if not cmd_input:
        print("\n错误：命令不能为空\n")
        return

    client = AgentMCPClient(cmd_input.split())
    
    try:
        while client.continue_testing:
            print("\n🚀 开始Agent MCP客户端测试...\n")
            success = await client.run_full_workflow()
            
            if not success:
                break
                
            # 如果完成了流程但需要继续测试，会在step_7_close中处理
            if not client.continue_testing:
                break
                
    except KeyboardInterrupt:
        print("\n正在关闭 Agent MCP 客户端...\n")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}\n")
    finally:
        if client.mcp_server:
            try:
                await client.mcp_server.__aexit__(None, None, None)
            except:
                pass
        print(">>> 程序已退出")

if __name__ == "__main__":
    # 检查依赖
    if not shutil.which("npx"):
        print("⚠️  警告：npx未安装，某些MCP服务器可能无法启动")
        print("   可以安装: npm install -g npx")
        print()
    
    asyncio.run(main()) 