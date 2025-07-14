#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端请求模拟
"""
import requests
import json

def test_frontend_request():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试前端请求模拟")
    print("=" * 60)
    
    # 1. 先登录获取Token
    print("\n1. 登录获取Token...")
    try:
        login_data = {
            "username": "user1",
            "password": "user123"
        }
        
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✓ 登录成功，获取到Token: {token[:20]}...")
            
            # 2. 使用Token获取试卷分配
            print("\n2. 使用Token获取试卷分配...")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.get(f"{base_url}/my-assignments", headers=headers)
            print(f"获取试卷分配状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ 试卷分配获取成功")
                print(f"  - 分配数量: {len(data)}")
                if data:
                    print(f"  - 第一个分配: {data[0]}")
            elif response.status_code == 401:
                print("✗ Token无效")
                print(f"错误详情: {response.text}")
            elif response.status_code == 500:
                print("✗ 服务器内部错误")
                print(f"错误详情: {response.text}")
            else:
                print(f"✗ 其他错误: {response.text}")
                
        else:
            print(f"✗ 登录失败: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_frontend_request() 