#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_backend_debug():
    """直接测试后端接口"""
    base_url = "http://localhost:8000"
    
    print("============================================================")
    print("直接测试后端接口")
    print("============================================================")
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{base_url}/login", data=login_data)
    print(f"登录状态码: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.json()}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ 登录成功，获取到token: {token[:20]}...")
    
    # 2. 直接测试 /results/by-user 接口
    print(f"\n2. 测试 /results/by-user 接口 (user_id=53)...")
    
    url = f"{base_url}/results/by-user"
    params = {"user_id": 53}
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"请求URL: {url}")
    print(f"请求参数: {params}")
    print("请查看后端控制台的调试输出...")
    
    response = requests.get(url, params=params, headers=headers)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 接口调用成功，返回 {len(data)} 条记录")
        for i, result in enumerate(data):
            print(f"   {i+1}. 试卷: {result['paper_name']}, 总分: {result['total_score']}")
    else:
        print(f"❌ 接口调用失败: {response.status_code}")
        print(f"错误详情: {response.text}")

if __name__ == "__main__":
    test_backend_debug() 