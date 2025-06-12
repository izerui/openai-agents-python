import json
import sys
import subprocess
import threading
import time

# MCP 协议说明
MCP_PROTOCOL_DOCS = {
    "initialize": """
### 步骤1：初始化连接
建立与 MCP 服务器的初始连接，声明客户端能力
    """,

    "initialized": """
### 步骤2：协议协商
通知服务器客户端已完成初始化（无需等待响应）
    """,

    "auth": """
### 步骤3：身份认证
提供客户端认证信息（大多数MCP服务器跳过此步骤）
    """,

    "tools/list": """
### 步骤4：获取工具列表
请求服务器返回所有可用的工具和功能
    """,

    "parse_tools": """
### 步骤5：工具列表解析
解析服务器返回的工具信息，为后续操作做准备
    """,

    "tools/call": """
### 步骤6：调用工具
使用解析的工具信息调用具体工具，保持连接活跃
    """,

    "close": """
### 步骤7：循环测试
测试其他MCP服务器或退出程序
    """
}

class MCPClient:
    def __init__(self, server_command):
        self.server_process = None
        self.server_command = server_command
        self.current_step = 1
        self.total_steps = 7
        self.available_tools = []
        self.current_request_id = 1
        self.continue_testing = True
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

    def print_protocol_doc(self, method):
        """打印协议说明"""
        if method in MCP_PROTOCOL_DOCS:
            print("协议说明:")
            print(MCP_PROTOCOL_DOCS[method])
            print()

    def get_next_request_id(self):
        """获取下一个请求ID"""
        self.current_request_id += 1
        return self.current_request_id

    def _send_init_message(self):
        """发送初始化消息"""
        self.print_step_header()
        self.print_protocol_doc("initialize")

        init_message = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                }
            },
            "id": self.current_request_id
        }
        self._send_request("initialize", init_message)

    def _send_request(self, method, request):
        """发送请求到服务器"""
        try:
            request_str = json.dumps(request) + "\n"
            print(f"\n>>> 发送请求 ({method}):")
            print(json.dumps(request, ensure_ascii=False, indent=2))
            print()

            self.server_process.stdin.write(request_str)
            self.server_process.stdin.flush()
        except Exception as e:
            print(f"\n错误：发送请求失败: {e}\n")

    def _read_output(self):
        """读取服务器输出"""
        while True:
            try:
                line = self.server_process.stdout.readline()
                if not line:
                    break

                try:
                    response = json.loads(line)
                    print(f"\n<<< 收到响应:")
                    print(json.dumps(response, ensure_ascii=False, indent=2))
                    print()

                    # 处理响应并发送下一个步骤的消息
                    self.handle_response(response)

                except json.JSONDecodeError as e:
                    print(f"\n错误：解析响应失败: {e}\n")
                    print(f"原始响应: {line}")

            except Exception as e:
                print(f"\n错误：读取响应失败: {e}\n")
                break

    def handle_response(self, response):
        """处理服务器响应"""
        current_method = self.protocol_steps[self.current_step - 1][0]
        
        # 如果是 tools/list 响应，保存工具列表
        if current_method == "tools/list" and "result" in response:
            if "tools" in response["result"]:
                self.available_tools = response["result"]["tools"]
                print(f"\n>>> 解析到 {len(self.available_tools)} 个可用工具:")
                for i, tool in enumerate(self.available_tools):
                    print(f"  {i+1}. {tool.get('name', 'Unknown')} - {tool.get('description', 'No description')}")
                print()

        # 发送下一个步骤的消息
        self.send_next_step()

    def send_next_step(self):
        """发送下一步骤的消息"""
        self.current_step += 1
        if self.current_step <= self.total_steps:
            # 在切换到新步骤前暂停1秒
            time.sleep(1)
            self.print_step_header()
            method = self.protocol_steps[self.current_step - 1][0]
            self.print_protocol_doc(method)

            if method == "initialized":
                # 步骤2：协议协商（通知消息，无需等待响应）
                self._send_request(method, {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": {}
                })
                # initialized 是通知消息，不等待响应，直接进入下一步
                print(">>> 已发送 initialized 通知，继续下一步...\n")
                time.sleep(1)
                self.send_next_step()
                return
            elif method == "auth":
                # 步骤3：身份认证（模拟，大多数MCP服务器不需要认证）
                print(">>> 注意：大多数 MCP 服务器不需要显式认证，跳过此步骤\n")
                time.sleep(1)
                self.send_next_step()
                return
            elif method == "tools/list":
                # 步骤4：获取工具列表
                self._send_request(method, {
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": {},
                    "id": self.get_next_request_id()
                })
            elif method == "parse_tools":
                # 步骤5：工具列表解析
                print(">>> 开始解析工具列表...")
                if self.available_tools:
                    print(f">>> 成功解析 {len(self.available_tools)} 个工具:")
                    for tool in self.available_tools:
                        print(f"  - 工具名称: {tool.get('name', 'Unknown')}")
                        print(f"    描述: {tool.get('description', 'No description')}")
                        if 'inputSchema' in tool:
                            print(f"    输入参数: {list(tool['inputSchema'].get('properties', {}).keys())}")
                        print()
                else:
                    print(">>> 警告：未获取到任何工具信息")
                print(">>> 工具解析完成\n")
                time.sleep(2)
                self.send_next_step()
                return
            elif method == "tools/call":
                # 步骤6：调用工具
                if self.available_tools:
                    # 调用第一个可用工具作为示例
                    first_tool = self.available_tools[0]
                    tool_name = first_tool.get('name')
                    print(f">>> 示例：调用工具 '{tool_name}'")
                    
                    # 构建工具调用请求
                    call_request = {
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": {}  # 简单示例，使用空参数
                        },
                        "id": self.get_next_request_id()
                    }
                    self._send_request("tools/call", call_request)
                else:
                    print(">>> 没有可用工具，跳过调用步骤\n")
                    time.sleep(1)
                    self.send_next_step()
                    return
            elif method == "close":
                # 步骤7：循环测试
                print(">>> 当前MCP服务器测试完成!")
                print("\n" + "="*60)
                print("          MCP 客户端交互流程完成!")
                print("="*60 + "\n")
                
                # 关闭当前服务器进程
                if self.server_process:
                    self.server_process.terminate()
                    self.server_process = None
                    print(">>> 当前服务器进程已终止\n")
                
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
                            # 重新开始测试流程
                            if self.start():
                                return
                        else:
                            print("命令为空，退出程序")
                            self.continue_testing = False
                    else:
                        print(">>> 退出程序")
                        self.continue_testing = False
                except (KeyboardInterrupt, EOFError):
                    print("\n>>> 用户中断，退出程序")
                    self.continue_testing = False
        else:
            print("\n>>> 所有步骤已完成!")

    def start(self):
        """启动客户端"""
        try:
            print(f"\n>>> 启动 MCP 服务器: {' '.join(self.server_command)}")
            self.server_process = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 等待服务器启动
            time.sleep(1)
            
            # 启动读取线程
            threading.Thread(target=self._read_output, daemon=True).start()

            # 发送初始化消息
            self._send_init_message()
            return True

        except Exception as e:
            print(f"\n错误：启动服务器失败: {e}\n")
            return False

    def close(self):
        """关闭客户端"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()

    def reset_for_new_test(self):
        """重置状态以便进行新的测试"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
        
        self.current_step = 1
        self.available_tools = []
        self.current_request_id = 1
        print("\n" + "="*60)
        print("          准备测试新的 MCP 服务器")
        print("="*60 + "\n")

def main():
    """主函数"""
    print("""
===========================================
          MCP 客户端启动向导
===========================================

本客户端将按照完整的 MCP 交互流程执行：
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

    client = MCPClient(cmd_input.split())
    
    try:
        while client.continue_testing:
            if client.start():
                print("\n正在运行 MCP 客户端...(按 Ctrl+C 退出)\n")
                # 等待所有步骤完成
                while client.current_step <= client.total_steps and client.continue_testing:
                    time.sleep(0.5)
                
                # 如果完成了所有步骤但仍要继续测试，等待用户输入
                if client.continue_testing and client.current_step > client.total_steps:
                    time.sleep(1)
            else:
                break
                
    except KeyboardInterrupt:
        print("\n正在关闭 MCP 客户端...\n")
    finally:
        client.close()
        print(">>> 程序已退出")

if __name__ == "__main__":
    main()
