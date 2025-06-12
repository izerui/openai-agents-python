#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP调试脚本 - 直接测试MCP工具调用
"""
import asyncio
import os
import shutil
import json

from agents.mcp import MCPServerStdio


async def test_mcp_directly():
    """直接测试MCP服务器的工具调用"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "sample_files")
    
    # 切换到samples目录，让MCP服务器以此作为工作目录
    original_cwd = os.getcwd()
    os.chdir(samples_dir)
    
    print(f"测试目录: {samples_dir}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"目录内容: {os.listdir('.')}")
    print("=" * 50)

    try:
        async with MCPServerStdio(
            name="Filesystem Server Debug",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],  # 使用当前目录
            },
        ) as server:
            print("✅ MCP服务器已启动")
            
            # 1. 测试获取工具列表
            print("\n1. 获取工具列表...")
            try:
                tools = await server.list_tools()
                print(f"✅ 成功获取 {len(tools)} 个工具:")
                for i, tool in enumerate(tools):
                    print(f"  {i+1}. {tool.name} - {tool.description}")
                    if hasattr(tool, 'inputSchema') and tool.inputSchema:
                        print(f"     参数: {list(tool.inputSchema.get('properties', {}).keys())}")
            except Exception as e:
                print(f"❌ 获取工具列表失败: {e}")
                return

            # 2. 测试列出目录
            print("\n2. 测试 list_directory 工具...")
            try:
                result = await server.call_tool("list_directory", {"path": ""})  # 使用空路径表示根目录
                print(f"✅ 列出目录成功:")
                print(f"   结果: {result}")
            except Exception as e:
                print(f"❌ 列出目录失败: {e}")

            # 3. 测试读取文件
            print("\n3. 测试 read_file 工具...")
            try:
                result = await server.call_tool("read_file", {"path": "favorite_books.txt"})  # 直接使用文件名
                print(f"✅ 读取文件成功:")
                print(f"   结果长度: {len(str(result))}")
                print(f"   内容预览: {str(result)[:200]}...")
            except Exception as e:
                print(f"❌ 读取文件失败: {e}")

            # 4. 测试读取歌曲文件
            print("\n4. 测试读取 favorite_songs.txt...")
            try:
                result = await server.call_tool("read_file", {"path": "favorite_songs.txt"})  # 直接使用文件名
                print(f"✅ 读取歌曲文件成功:")
                print(f"   结果: {result}")
            except Exception as e:
                print(f"❌ 读取歌曲文件失败: {e}")

            # 5. 测试获取允许的目录
            print("\n5. 测试获取允许的目录...")
            try:
                result = await server.call_tool("list_allowed_directories", {})
                print(f"✅ 获取允许目录成功:")
                print(f"   结果: {result}")
            except Exception as e:
                print(f"❌ 获取允许目录失败: {e}")

            print("\n" + "=" * 50)
            print("✅ MCP直接调用测试完成")
    finally:
        # 恢复原始工作目录
        os.chdir(original_cwd)


if __name__ == "__main__":
    if not shutil.which("npx"):
        print("❌ npx未安装，请先安装: npm install -g npx")
        exit(1)
    
    print("🚀 开始MCP直接调用测试...\n")
    asyncio.run(test_mcp_directly()) 