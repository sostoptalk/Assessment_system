#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def debug_score_calculation():
    """调试算分逻辑"""
    base_url = "http://localhost:8000"
    
    print("============================================================")
    print("调试算分逻辑")
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
    
    # 2. 获取用户列表，找到user5
    print("\n2. 获取用户列表...")
    headers = {"Authorization": f"Bearer {token}"}
    users_response = requests.get(f"{base_url}/users", headers=headers)
    print(f"获取用户列表状态码: {users_response.status_code}")
    
    if users_response.status_code != 200:
        print(f"❌ 获取用户列表失败: {users_response.json()}")
        return
    
    users = users_response.json()
    user5 = None
    for user in users:
        if user.get('username') == 'user5':
            user5 = user
            break
    
    if not user5:
        print("❌ 没有找到user5")
        return
    
    user_id = user5['id']
    print(f"✅ 找到user5: {user5.get('real_name', user5['username'])} (ID: {user_id})")
    
    # 3. 获取user5的试卷分配
    print(f"\n3. 获取user5的试卷分配...")
    assignments_response = requests.get(f"{base_url}/my-assignments", headers=headers)
    print(f"获取试卷分配状态码: {assignments_response.status_code}")
    
    if assignments_response.status_code != 200:
        print(f"❌ 获取试卷分配失败: {assignments_response.json()}")
        return
    
    assignments = assignments_response.json()
    print(f"✅ 获取试卷分配成功，共 {len(assignments)} 个分配")
    
    # 4. 测试 /results/by-user 接口
    print(f"\n4. 测试 /results/by-user 接口 (user_id={user_id})...")
    
    url = f"{base_url}/results/by-user"
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
            print(f"      大维度数量: {len(result['big_dimensions'])}")
            for j, dim in enumerate(result['big_dimensions']):
                print(f"        {j+1}. {dim['name']}: {dim['score']}")
                if dim.get('sub_dimensions'):
                    for k, sub in enumerate(dim['sub_dimensions']):
                        print(f"          {k+1}. {sub['name']}: {sub['score']}")
    else:
        print(f"❌ 接口调用失败: {response.status_code}")
        print(f"错误详情: {response.text}")

if __name__ == "__main__":
    debug_score_calculation() 