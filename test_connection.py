#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前后端连接
"""

import requests
import time

def test_backend():
    """测试后端连接"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ 后端连接成功: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_frontend():
    """测试前端连接"""
    try:
        response = requests.get("http://localhost:3001/", timeout=5)
        print(f"✅ 前端连接成功: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def test_backend_api():
    """测试后端API"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ 后端API文档可访问: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端API文档访问失败: {e}")
        return False

def main():
    print("🔍 开始测试前后端连接...")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 测试后端
    print("\n📦 测试后端服务...")
    backend_ok = test_backend()
    
    # 测试前端
    print("\n🎨 测试前端服务...")
    frontend_ok = test_frontend()
    
    # 测试后端API
    print("\n🔧 测试后端API...")
    api_ok = test_backend_api()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"后端API: {'✅ 正常' if api_ok else '❌ 异常'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 前后端服务都正常运行！")
        print("🌐 请访问以下地址:")
        print("   前端: http://localhost:3001")
        print("   后端API文档: http://localhost:8000/docs")
    else:
        print("\n⚠️  存在问题，请检查:")
        if not backend_ok:
            print("   - 后端服务是否在 http://localhost:8000 运行")
        if not frontend_ok:
            print("   - 前端服务是否在 http://localhost:3001 运行")

if __name__ == "__main__":
    main() 