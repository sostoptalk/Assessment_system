#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_frontend_proxy():
    """测试前端代理配置"""
    base_url = "http://localhost:3000"  # 前端地址
    
    print("============================================================")
    print("测试前端代理配置")
    print("============================================================")
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{base_url}/api/login", data=login_data)
    print(f"登录状态码: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.json()}")
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ 登录成功，获取到token: {token[:20]}...")
    
    # 2. 获取用户列表
    print("\n2. 获取用户列表...")
    headers = {"Authorization": f"Bearer {token}"}
    users_response = requests.get(f"{base_url}/api/users", headers=headers)
    print(f"获取用户列表状态码: {users_response.status_code}")
    
    if users_response.status_code != 200:
        print(f"❌ 获取用户列表失败: {users_response.json()}")
        return
    
    users = users_response.json()
    participants = [u for u in users if u.get('role') == 'participant']
    print(f"✅ 获取用户列表成功，共 {len(users)} 个用户，其中被试者 {len(participants)} 个")
    
    if not participants:
        print("❌ 没有找到被试者")
        return
    
    # 选择第一个被试者进行测试
    test_user = participants[0]
    user_id = test_user['id']
    print(f"   测试被试者: {test_user.get('real_name', test_user['username'])} (ID: {user_id})")
    
    # 3. 测试 /api/results/by-user 接口（通过前端代理）
    print(f"\n3. 测试 /api/results/by-user 接口 (user_id={user_id})...")
    
    url = f"{base_url}/api/results/by-user"
    params = {"user_id": user_id}
    
    print(f"请求URL: {url}")
    print(f"请求参数: {params}")
    
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
    test_frontend_proxy() 