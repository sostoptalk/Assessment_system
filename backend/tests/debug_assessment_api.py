#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试被试者测试API
"""
import requests
import json

def debug_assessment_api():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("调试被试者测试API")
    print("=" * 60)
    
    # 1. 测试获取试卷分配（带详细错误信息）
    print("\n1. 测试获取试卷分配...")
    try:
        response = requests.get(f"{base_url}/my-assignments")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ 试卷分配获取成功")
            print(f"  - 分配数量: {len(data)}")
        elif response.status_code == 401:
            print("✗ 需要认证Token")
        elif response.status_code == 500:
            print("✗ 服务器内部错误")
            print(f"错误详情: {response.text}")
        else:
            print(f"✗ 其他错误: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 测试其他API是否正常
    print("\n2. 测试其他API...")
    try:
        response = requests.get(f"{base_url}/me")
        print(f"GET /me 状态码: {response.status_code}")
        
        response = requests.get(f"{base_url}/dashboard/stats")
        print(f"GET /dashboard/stats 状态码: {response.status_code}")
        
        response = requests.get(f"{base_url}/papers")
        print(f"GET /papers 状态码: {response.status_code}")
        
    except Exception as e:
        print(f"✗ 其他API测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("调试完成")

if __name__ == "__main__":
    debug_assessment_api() 