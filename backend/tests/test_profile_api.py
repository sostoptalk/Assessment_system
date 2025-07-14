#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户信息更新API
"""
import requests
import json

def test_profile_api():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("用户信息更新API测试")
    print("=" * 60)
    
    # 1. 测试获取用户信息
    print("\n1. 测试获取用户信息...")
    try:
        response = requests.get(f"{base_url}/me")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ 用户信息获取成功")
            print(f"  - 用户名: {data['username']}")
            print(f"  - 真实姓名: {data['real_name']}")
            print(f"  - 邮箱: {data['email']}")
            print(f"  - 手机号: {data['phone']}")
            print(f"  - 角色: {data['role']}")
        else:
            print(f"✗ 获取用户信息失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("注意: 更新API需要登录Token，请在浏览器中测试")

if __name__ == "__main__":
    test_profile_api() 