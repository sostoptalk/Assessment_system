import requests
import json

BASE_URL = "http://localhost:8000"

def check_admin_user():
    print("=== 检查admin用户 ===")
    
    # 1. 尝试登录
    print("\n1. 尝试登录admin用户")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✅ 登录成功，获取到token: {token[:20]}...")
        
        # 2. 使用token获取用户信息
        print("\n2. 使用token获取用户信息")
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"获取用户信息状态码: {me_response.status_code}")
        print(f"用户信息: {me_response.text}")
        
    else:
        print("❌ 登录失败")
        
        # 3. 尝试注册admin用户
        print("\n3. 尝试注册admin用户")
        register_data = {
            "username": "admin",
            "password": "admin123",
            "real_name": "管理员",
            "role": "admin"
        }
        
        register_response = requests.post(f"{BASE_URL}/register", params=register_data)
        print(f"注册响应状态码: {register_response.status_code}")
        print(f"注册响应内容: {register_response.text}")
        
        if register_response.status_code == 200:
            print("✅ admin用户注册成功，请重新尝试登录")

if __name__ == "__main__":
    check_admin_user() 