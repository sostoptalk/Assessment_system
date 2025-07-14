#!/usr/bin/env python3
"""
测试题目乱序功能
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test123"

def login(username, password):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/login", data={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.text}")
        return None

def test_shuffle_function():
    """测试乱序功能"""
    print("=== 测试题目乱序功能 ===")
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    admin_token = login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("管理员登录失败，退出测试")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. 获取试卷列表
    print("\n2. 获取试卷列表...")
    response = requests.get(f"{BASE_URL}/papers/", headers=headers)
    if response.status_code != 200:
        print(f"获取试卷列表失败: {response.text}")
        return
    
    papers = response.json()
    if not papers:
        print("没有找到试卷，请先创建试卷")
        return
    
    paper = papers[0]  # 使用第一个试卷
    paper_id = paper["id"]
    print(f"使用试卷: {paper['name']} (ID: {paper_id})")
    
    # 3. 获取试卷题目
    print("\n3. 获取试卷题目...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions", headers=headers)
    if response.status_code != 200:
        print(f"获取试卷题目失败: {response.text}")
        return
    
    questions_data = response.json()
    questions = questions_data.get("questions", [])
    print(f"试卷共有 {len(questions)} 道题目")
    
    if len(questions) < 2:
        print("试卷题目数量不足，无法测试乱序功能")
        return
    
    # 4. 获取当前乱序状态
    print("\n4. 获取当前乱序状态...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/shuffle-status", headers=headers)
    if response.status_code == 200:
        shuffle_status = response.json()
        print(f"当前乱序状态: {'已启用' if shuffle_status['is_shuffled'] else '未启用'}")
        if shuffle_status['is_shuffled']:
            print(f"乱序种子: {shuffle_status['shuffle_seed']}")
    else:
        print(f"获取乱序状态失败: {response.text}")
    
    # 5. 启用乱序
    print("\n5. 启用题目乱序...")
    response = requests.post(
        f"{BASE_URL}/papers/{paper_id}/shuffle-questions",
        headers=headers,
        json={"enable_shuffle": True}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"乱序启用成功: {result['message']}")
        print(f"乱序种子: {result['shuffle_seed']}")
        print(f"题目数量: {result['question_count']}")
        print(f"乱序顺序: {result['shuffled_order'][:5]}...")  # 只显示前5个
    else:
        print(f"启用乱序失败: {response.text}")
        return
    
    # 6. 再次获取乱序状态
    print("\n6. 验证乱序状态...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/shuffle-status", headers=headers)
    if response.status_code == 200:
        shuffle_status = response.json()
        print(f"乱序状态: {'已启用' if shuffle_status['is_shuffled'] else '未启用'}")
        if shuffle_status['is_shuffled']:
            print(f"乱序种子: {shuffle_status['shuffle_seed']}")
    else:
        print(f"获取乱序状态失败: {response.text}")
    
    # 7. 获取乱序后的题目
    print("\n7. 获取乱序后的题目...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions", headers=headers)
    if response.status_code == 200:
        questions_data = response.json()
        questions = questions_data.get("questions", [])
        print(f"乱序后题目数量: {len(questions)}")
        
        # 显示前5道题的顺序
        print("前5道题:")
        for i, q in enumerate(questions[:5]):
            print(f"  题目{i+1}: ID={q['id']}, 原始顺序={q.get('original_order', 'N/A')}")
    else:
        print(f"获取乱序题目失败: {response.text}")
    
    # 8. 测试用户登录
    print("\n8. 测试用户登录...")
    user_token = login(TEST_USERNAME, TEST_PASSWORD)
    if not user_token:
        print("测试用户登录失败")
        return
    
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 9. 获取用户ID
    print("\n9. 获取用户信息...")
    response = requests.get(f"{BASE_URL}/users/me", headers=user_headers)
    if response.status_code == 200:
        user_info = response.json()
        user_id = user_info["id"]
        print(f"用户ID: {user_id}")
    else:
        print(f"获取用户信息失败: {response.text}")
        return
    
    # 10. 获取用户的题目顺序（带用户ID）
    print("\n10. 获取用户的题目顺序...")
    response = requests.get(
        f"{BASE_URL}/papers/{paper_id}/questions?user_id={user_id}",
        headers=user_headers
    )
    if response.status_code == 200:
        questions_data = response.json()
        questions = questions_data.get("questions", [])
        print(f"用户题目数量: {len(questions)}")
        print(f"是否启用乱序: {questions_data.get('is_shuffled', False)}")
        
        # 显示前5道题的顺序
        print("用户前5道题:")
        for i, q in enumerate(questions[:5]):
            print(f"  题目{i+1}: ID={q['id']}, 显示顺序={q['order_num']}, 原始顺序={q.get('original_order', 'N/A')}")
    else:
        print(f"获取用户题目失败: {response.text}")
    
    # 11. 禁用乱序
    print("\n11. 禁用题目乱序...")
    response = requests.post(
        f"{BASE_URL}/papers/{paper_id}/shuffle-questions",
        headers=headers,
        json={"enable_shuffle": False}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"乱序禁用成功: {result['message']}")
    else:
        print(f"禁用乱序失败: {response.text}")
    
    # 12. 验证禁用后的状态
    print("\n12. 验证禁用后的状态...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/shuffle-status", headers=headers)
    if response.status_code == 200:
        shuffle_status = response.json()
        print(f"乱序状态: {'已启用' if shuffle_status['is_shuffled'] else '未启用'}")
    else:
        print(f"获取乱序状态失败: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_shuffle_function() 