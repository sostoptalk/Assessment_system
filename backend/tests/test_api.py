# -*- coding: utf-8 -*-
"""
API测试脚本
测试后端接口功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_login():
    """测试登录接口"""
    print("=== 测试登录接口 ===")
    
    # 测试管理员登录
    print("1. 管理员登录测试")
    admin_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/login", json=admin_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        print(f"管理员Token: {admin_token[:20]}...")
    else:
        admin_token = None
    print()
    
    # 测试普通用户登录
    print("2. 普通用户登录测试")
    user_data = {"username": "user1", "password": "user123"}
    response = requests.post(f"{BASE_URL}/login", json=user_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        user_token = response.json().get("access_token")
        print(f"用户Token: {user_token[:20]}...")
    else:
        user_token = None
    print()
    
    return admin_token, user_token

def test_user_info(admin_token, user_token):
    """测试获取用户信息接口"""
    print("=== 测试获取用户信息接口 ===")
    
    if admin_token:
        print("1. 管理员信息获取")
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()
    
    if user_token:
        print("2. 普通用户信息获取")
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print()

def test_assessment_questions():
    """测试获取测评问题接口"""
    print("=== 测试获取测评问题接口 ===")
    response = requests.get(f"{BASE_URL}/assessment/questions")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    print()

def test_assessment_submit():
    """测试提交测评接口"""
    print("=== 测试提交测评接口 ===")
    answers = {
        "answers": [
            {"question_id": 1, "answer": "数据分析驱动"},
            {"question_id": 2, "answer": "立即调整策略"}
        ]
    }
    response = requests.post(f"{BASE_URL}/assessment/submit", json=answers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

def test_cors():
    """测试CORS配置"""
    print("=== 测试CORS配置 ===")
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    response = requests.options(f"{BASE_URL}/login", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"CORS Headers: {dict(response.headers)}")
    print()

def main():
    """主测试函数"""
    print("开始API测试...")
    print("=" * 50)
    
    try:
        # 测试健康检查
        test_health()
        
        # 测试登录
        admin_token, user_token = test_login()
        
        # 测试用户信息获取
        test_user_info(admin_token, user_token)
        
        # 测试测评相关接口
        test_assessment_questions()
        test_assessment_submit()
        
        # 测试CORS
        test_cors()
        
        print("=" * 50)
        print("API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到后端服务，请确保后端服务正在运行在 http://localhost:8000")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 