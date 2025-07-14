#!/usr/bin/env python3
"""
测试维度题目匹配功能
"""

import requests
import json

# 测试维度题目匹配逻辑
def test_dimension_question_matching():
    base_url = "http://localhost:8000"
    
    print("=== 测试维度题目匹配逻辑 ===")
    
    # 1. 获取试卷列表
    print("\n1. 获取试卷列表...")
    response = requests.get(f"{base_url}/papers/")
    if response.status_code == 200:
        papers = response.json()
        if papers:
            paper_id = papers[0]['id']
            print(f"使用试卷ID: {paper_id}")
        else:
            print("没有找到试卷")
            return
    else:
        print("获取试卷失败")
        return
    
    # 2. 获取试卷维度
    print("\n2. 获取试卷维度...")
    response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
    if response.status_code == 200:
        dimensions = response.json()
        print(f"找到 {len(dimensions)} 个维度")
        for dim in dimensions:
            print(f"  - {dim['name']} (ID: {dim['id']})")
            if dim.get('children'):
                for child in dim['children']:
                    print(f"    └─ {child['name']} (ID: {child['id']})")
    else:
        print("获取维度失败")
        return
    
    # 3. 测试获取可匹配题目
    print("\n3. 测试获取可匹配题目...")
    for dim in dimensions:
        print(f"\n测试维度: {dim['name']} (ID: {dim['id']})")
        
        # 检查是否有子维度
        has_children = bool(dim.get('children') and len(dim['children']) > 0)
        print(f"  有子维度: {has_children}")
        
        if has_children:
            print("  跳过父维度（应该有子维度）")
            continue
            
        response = requests.get(f"{base_url}/dimensions/{dim['id']}/available-questions?paper_id={paper_id}")
        if response.status_code == 200:
            questions = response.json()
            print(f"  可匹配题目数: {len(questions)}")
            if questions:
                print(f"  示例题目: {questions[0]['content'][:50]}...")
        elif response.status_code == 400:
            error_data = response.json()
            print(f"  错误: {error_data.get('detail', '未知错误')}")
        else:
            print(f"  请求失败: {response.status_code}")
    
    # 4. 测试子维度的可匹配题目
    print("\n4. 测试子维度的可匹配题目...")
    for dim in dimensions:
        if dim.get('children'):
            for child in dim['children']:
                print(f"\n测试子维度: {child['name']} (ID: {child['id']})")
                
                response = requests.get(f"{base_url}/dimensions/{child['id']}/available-questions?paper_id={paper_id}")
                if response.status_code == 200:
                    questions = response.json()
                    print(f"  可匹配题目数: {len(questions)}")
                    if questions:
                        print(f"  示例题目: {questions[0]['content'][:50]}...")
                elif response.status_code == 400:
                    error_data = response.json()
                    print(f"  错误: {error_data.get('detail', '未知错误')}")
                else:
                    print(f"  请求失败: {response.status_code}")

if __name__ == "__main__":
    test_dimension_question_matching() 