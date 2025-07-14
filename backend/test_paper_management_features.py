#!/usr/bin/env python3
"""
测试试卷管理界面的新功能
包括：题目编辑、手动添加题目选项乱序、Word导入选项乱序
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

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

def test_paper_management_features():
    """测试试卷管理界面的新功能"""
    print("=== 测试试卷管理界面新功能 ===")
    
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
    
    # 3. 测试手动添加题目（带选项乱序）
    print("\n3. 测试手动添加题目（带选项乱序）...")
    test_question = {
        "content": "测试手动添加题目（选项乱序）",
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
        
        # 将题目添加到试卷
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
    else:
        print(f"创建题目失败: {response.text}")
    
    # 4. 测试编辑题目
    print("\n4. 测试编辑题目...")
    updated_question = {
        "content": "已编辑的题目（选项乱序）",
        "type": "single",
        "options": ["选项A", "选项B", "选项C", "选项D"],
        "scores": [10, 7, 4, 1],
        "shuffle_options": True
    }
    
    response = requests.put(f"{BASE_URL}/questions/{question_id}", 
                           json=updated_question, headers=headers)
    if response.status_code == 200:
        updated_data = response.json()
        print(f"题目编辑成功，ID: {updated_data['id']}")
        print(f"新内容: {updated_data['content']}")
        print(f"选项乱序设置: {updated_data['shuffle_options']}")
    else:
        print(f"编辑题目失败: {response.text}")
    
    # 5. 获取试卷题目列表
    print("\n5. 获取试卷题目列表...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions", headers=headers)
    if response.status_code == 200:
        questions_data = response.json()
        questions = questions_data.get("questions", [])
        print(f"试卷共有 {len(questions)} 道题目")
        
        for i, q in enumerate(questions):
            print(f"题目{i+1}: {q['content']}")
            print(f"  选项乱序: {q.get('shuffle_options', False)}")
            print(f"  选项: {q['options']}")
            print(f"  分数: {q['scores']}")
    else:
        print(f"获取试卷题目失败: {response.text}")
    
    # 6. 测试创建另一个题目（不启用选项乱序）
    print("\n6. 测试创建题目（不启用选项乱序）...")
    test_question2 = {
        "content": "测试题目（不启用选项乱序）",
        "type": "multiple",
        "options": ["选项A", "选项B", "选项C", "选项D"],
        "scores": [10, 7, 4, 1],
        "shuffle_options": False
    }
    
    response = requests.post(f"{BASE_URL}/questions", json=test_question2, headers=headers)
    if response.status_code == 200:
        question_data2 = response.json()
        question_id2 = question_data2["id"]
        print(f"创建题目成功，ID: {question_id2}")
        print(f"选项乱序设置: {question_data2['shuffle_options']}")
        
        # 将题目添加到试卷
        add_question_data2 = [{
            "question_id": question_id2,
            "dimension_id": None
        }]
        
        response = requests.post(f"{BASE_URL}/papers/{paper_id}/questions/", 
                               json=add_question_data2, headers=headers)
        if response.status_code == 200:
            print("题目添加成功")
        else:
            print(f"添加题目失败: {response.text}")
    else:
        print(f"创建题目失败: {response.text}")
    
    # 7. 再次获取试卷题目列表，验证两种设置
    print("\n7. 验证试卷题目列表...")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions", headers=headers)
    if response.status_code == 200:
        questions_data = response.json()
        questions = questions_data.get("questions", [])
        print(f"试卷共有 {len(questions)} 道题目")
        
        shuffle_enabled = 0
        shuffle_disabled = 0
        
        for i, q in enumerate(questions):
            if q.get('shuffle_options', False):
                shuffle_enabled += 1
                print(f"题目{i+1}: {q['content']} [选项乱序已启用]")
            else:
                shuffle_disabled += 1
                print(f"题目{i+1}: {q['content']} [选项乱序未启用]")
        
        print(f"\n统计:")
        print(f"  启用选项乱序的题目: {shuffle_enabled}")
        print(f"  未启用选项乱序的题目: {shuffle_disabled}")
    else:
        print(f"获取试卷题目失败: {response.text}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_paper_management_features() 