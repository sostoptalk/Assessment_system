#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端服务诊断脚本
"""

import requests
import subprocess
import sys
import time
import os

def check_port(port):
    """检查端口是否被占用"""
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        return f':{port}' in result.stdout
    except:
        return False

def test_http_connection(url, timeout=5):
    """测试HTTP连接"""
    try:
        response = requests.get(url, timeout=timeout)
        return True, response.status_code, response.text[:200]
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

def check_process(process_name):
    """检查进程是否运行"""
    try:
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        return process_name in result.stdout
    except:
        return False

def main():
    print("🔍 前端服务诊断开始...")
    print("=" * 60)
    
    # 检查Node.js
    print("\n📦 检查Node.js环境...")
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js版本: {result.stdout.strip()}")
        else:
            print("❌ Node.js未安装或无法访问")
            return
    except:
        print("❌ Node.js未安装")
        return
    
    # 检查npm
    print("\n📦 检查npm...")
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm版本: {result.stdout.strip()}")
        else:
            print("❌ npm未安装或无法访问")
            return
    except:
        print("❌ npm未安装")
        return
    
    # 检查前端目录
    print("\n📁 检查前端目录...")
    frontend_dir = "frontend"
    if os.path.exists(frontend_dir):
        print(f"✅ 前端目录存在: {frontend_dir}")
        
        # 检查关键文件
        key_files = [
            "package.json",
            "vite.config.ts",
            "src/main.tsx",
            "src/App.tsx",
            "public/index.html"
        ]
        
        for file in key_files:
            file_path = os.path.join(frontend_dir, file)
            if os.path.exists(file_path):
                print(f"✅ {file} 存在")
            else:
                print(f"❌ {file} 不存在")
    else:
        print(f"❌ 前端目录不存在: {frontend_dir}")
        return
    
    # 检查端口占用
    print("\n🔌 检查端口占用...")
    ports = [3000, 3001, 3002, 3003]
    for port in ports:
        if check_port(port):
            print(f"⚠️  端口 {port} 被占用")
        else:
            print(f"✅ 端口 {port} 可用")
    
    # 测试HTTP连接
    print("\n🌐 测试HTTP连接...")
    urls = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ]
    
    for url in urls:
        success, status_code, response_text = test_http_connection(url, timeout=3)
        if success:
            print(f"✅ {url} - 状态码: {status_code}")
            if "人才测评平台" in response_text or "React" in response_text:
                print(f"   📄 内容: 前端应用页面")
            else:
                print(f"   📄 内容: {response_text[:50]}...")
        else:
            print(f"❌ {url} - 错误: {response_text}")
    
    # 检查防火墙
    print("\n🛡️  检查防火墙状态...")
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                              capture_output=True, text=True)
        if "ON" in result.stdout:
            print("⚠️  防火墙已启用，可能阻止连接")
        else:
            print("✅ 防火墙未启用")
    except:
        print("❓ 无法检查防火墙状态")
    
    print("\n" + "=" * 60)
    print("📋 诊断建议:")
    print("1. 如果端口被占用，请终止占用进程")
    print("2. 如果防火墙阻止，请添加例外规则")
    print("3. 尝试使用 127.0.0.1 替代 localhost")
    print("4. 检查浏览器是否阻止了连接")
    print("5. 尝试使用不同的浏览器")

if __name__ == "__main__":
    main() 