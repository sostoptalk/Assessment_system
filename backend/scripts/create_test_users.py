# -*- coding: utf-8 -*-
"""
创建测试用户账号脚本
通过API接口注册测试用户
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_users():
    """创建测试用户账号"""
    print("开始创建测试用户账号...")
    print("=" * 50)
    
    # 测试用户列表
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "real_name": "系统管理员",
            "role": "admin",
            "email": "admin@example.com"
        },
        {
            "username": "user1",
            "password": "user123",
            "real_name": "测试用户1",
            "role": "participant",
            "email": "user1@example.com"
        },
        {
            "username": "user2",
            "password": "user123",
            "real_name": "测试用户2",
            "role": "participant",
            "email": "user2@example.com"
        }
    ]
    
    for user in test_users:
        print(f"正在创建用户: {user['username']}")
        
        try:
            # 调用注册接口
            response = requests.post(
                f"{BASE_URL}/register",
                params={
                    "username": user["username"],
                    "password": user["password"],
                    "real_name": user["real_name"],
                    "role": user["role"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 用户 {user['username']} 创建成功！用户ID: {result.get('user_id')}")
            else:
                error_msg = response.json().get('detail', '未知错误')
                print(f"❌ 用户 {user['username']} 创建失败: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到后端服务，请确保后端服务正在运行在 {BASE_URL}")
            break
        except Exception as e:
            print(f"❌ 创建用户 {user['username']} 时出现错误: {e}")
        
        print("-" * 30)
    
    print("=" * 50)
    print("测试用户创建完成！")
    print("\n可用测试账号:")
    print("1. 管理员账号:")
    print("   用户名: admin")
    print("   密码: admin123")
    print("2. 普通用户账号:")
    print("   用户名: user1")
    print("   密码: user123")
    print("   用户名: user2")
    print("   密码: user123")

if __name__ == "__main__":
    create_test_users() 