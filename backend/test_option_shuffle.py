#!/usr/bin/env python3
"""
测试选项乱序功能
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

def test_option_shuffle_function():
    """测试选项乱序功能"""
    print("=== 测试选项乱序功能 ===")
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    admin_token = login(ADMIN_USERNAME, ADMIN_PASSWORD)
    if not admin_token:
        print("管理员登录失败，退出测试")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. 创建测试题目（启用选项乱序）
    print("\n2. 创建测试题目...")
    test_question = {
        "content": "测试选项乱序题目",
        "type": "single",
        "options": ["选项A", "选项B", "选项C", "选项D"],
        "scores": [10, 7, 4, 1],
        "shuffle_options": True
    }
    
    response = requests.post(f"{BASE_URL}/questions", json=test_question, headers=headers)
    if response.status_code == 200:
        question_data = response.json()
        question_id = question_data["id"]
        print(f"创建题目成功，ID: {question_id}")
        print(f"选项乱序设置: {question_data['shuffle_options']}")
    else:
        print(f"创建题目失败: {response.text}")
        return
    
    # 3. 获取试卷列表
    print("\n3. 获取试卷列表...")
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
    
    # 4. 将测试题目添加到试卷
    print("\n4. 将测试题目添加到试卷...")
    add_question_data = [{
        "question_id": question_id,
        "dimension_id": None
    }]
    
    response = requests.post(f"{BASE_URL}/papers/{paper_id}/questions/", 
                           json=add_question_data, headers=headers)
    if response.status_code == 200:
        print("题目添加成功")
    else:
        print(f"添加题目失败: {response.text}")
        return
    
    # 5. 测试用户登录
    print("\n5. 测试用户登录...")
    user_token = login(TEST_USERNAME, TEST_PASSWORD)
    if not user_token:
        print("测试用户登录失败")
        return
    
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # 6. 获取用户信息
    print("\n6. 获取用户信息...")
    response = requests.get(f"{BASE_URL}/users/me", headers=user_headers)
    if response.status_code == 200:
        user_info = response.json()
        user_id = user_info["id"]
        print(f"用户ID: {user_id}")
    else:
        print(f"获取用户信息失败: {response.text}")
        return
    
    # 7. 获取试卷分配
    print("\n7. 获取试卷分配...")
    response = requests.get(f"{BASE_URL}/my-assignments", headers=user_headers)
    if response.status_code == 200:
        assignments = response.json()
        assignment = None
        for a in assignments:
            if a["paper_id"] == paper_id:
                assignment = a
                break
        
        if assignment:
            assignment_id = assignment["id"]
            print(f"找到试卷分配，ID: {assignment_id}")
        else:
            print("未找到试卷分配，需要先分配试卷")
            return
    else:
        print(f"获取试卷分配失败: {response.text}")
        return
    
    # 8. 生成选项顺序
    print("\n8. 生成选项顺序...")
    response = requests.post(f"{BASE_URL}/assignments/{assignment_id}/generate-option-orders", 
                           headers=user_headers)
    if response.status_code == 200:
        result = response.json()
        print(f"选项顺序生成成功: {result['message']}")
        print(f"选项顺序: {result['option_orders']}")
    else:
        print(f"生成选项顺序失败: {response.text}")
        return
    
    # 9. 获取带选项乱序的题目
    print("\n9. 获取带选项乱序的题目...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions-with-options?user_id={user_id}", 
                          headers=user_headers)
    if response.status_code == 200:
        data = response.json()
        questions = data.get("questions", [])
        print(f"获取到 {len(questions)} 道题目")
        
        for i, q in enumerate(questions):
            print(f"\n题目{i+1}: {q['content']}")
            print(f"选项乱序: {q['shuffle_options']}")
            print(f"选项: {q['options']}")
            print(f"分数: {q['scores']}")
    else:
        print(f"获取题目失败: {response.text}")
    
    # 10. 再次生成选项顺序（验证一致性）
    print("\n10. 再次生成选项顺序（验证一致性）...")
    response = requests.post(f"{BASE_URL}/assignments/{assignment_id}/generate-option-orders", 
                           headers=user_headers)
    if response.status_code == 200:
        result = response.json()
        print(f"选项顺序生成成功: {result['message']}")
        print(f"选项顺序: {result['option_orders']}")
    else:
        print(f"生成选项顺序失败: {response.text}")
    
    # 11. 再次获取题目（验证选项顺序一致）
    print("\n11. 再次获取题目（验证选项顺序一致）...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions-with-options?user_id={user_id}", 
                          headers=user_headers)
    if response.status_code == 200:
        data = response.json()
        questions = data.get("questions", [])
        
        for i, q in enumerate(questions):
            print(f"\n题目{i+1}: {q['content']}")
            print(f"选项: {q['options']}")
            print(f"分数: {q['scores']}")
    else:
        print(f"获取题目失败: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_option_shuffle_function() 