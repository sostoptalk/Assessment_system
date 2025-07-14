# -*- coding: utf-8 -*-
"""
测试正式后端（连接数据库）
验证测试用户是否可以正常登录
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_real_backend():
    """测试正式后端功能"""
    print("开始测试正式后端（数据库连接）...")
    print("=" * 50)
    
    # 测试用户列表
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "description": "管理员账号"
        },
        {
            "username": "user1", 
            "password": "user123",
            "description": "普通用户账号1"
        },
        {
            "username": "user2",
            "password": "user123", 
            "description": "普通用户账号2"
        }
    ]
    
    tokens = {}
    
    for user in test_users:
        print(f"测试 {user['description']}: {user['username']}")
        
        try:
            # 测试登录
            login_data = {
                "username": user["username"],
                "password": user["password"]
            }
            
            # 使用表单数据格式（OAuth2PasswordRequestForm要求）
            response = requests.post(
                f"{BASE_URL}/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            print(f"登录状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("access_token")
                tokens[user["username"]] = token
                print(f"✅ 登录成功！Token: {token[:20]}...")
                
                # 测试获取用户信息
                headers = {"Authorization": f"Bearer {token}"}
                user_info_response = requests.get(f"{BASE_URL}/me", headers=headers)
                
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    print(f"✅ 用户信息获取成功: {user_info}")
                else:
                    print(f"❌ 用户信息获取失败: {user_info_response.json()}")
                    
            else:
                error_msg = response.json().get('detail', '未知错误')
                print(f"❌ 登录失败: {error_msg}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到后端服务，请确保后端服务正在运行在 {BASE_URL}")
            break
        except Exception as e:
            print(f"❌ 测试用户 {user['username']} 时出现错误: {e}")
        
        print("-" * 30)
    
    print("=" * 50)
    print("正式后端测试完成！")
    
    if tokens:
        print("\n✅ 所有测试用户都可以正常登录！")
        print("现在你可以：")
        print("1. 启动前端服务: npm run dev")
        print("2. 在浏览器中访问前端页面")
        print("3. 使用以下账号登录测试:")
        for user in test_users:
            print(f"   - {user['description']}: {user['username']} / {user['password']}")
    else:
        print("\n❌ 测试失败，请检查数据库连接和用户数据")

if __name__ == "__main__":
    test_real_backend() 