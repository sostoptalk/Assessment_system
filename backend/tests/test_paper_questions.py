#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试试卷题目API
"""
import requests
import json

def test_paper_questions():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试试卷题目API")
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
            
            # 2. 获取试卷分配
            print("\n2. 获取试卷分配...")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            response = requests.get(f"{base_url}/my-assignments", headers=headers)
            print(f"获取试卷分配状态码: {response.status_code}")
            
            if response.status_code == 200:
                assignments = response.json()
                print(f"✓ 试卷分配获取成功，数量: {len(assignments)}")
                
                if assignments:
                    # 3. 获取第一个试卷的题目
                    paper_id = assignments[0]["paper_id"]
                    print(f"\n3. 获取试卷 {paper_id} 的题目...")
                    
                    response = requests.get(f"{base_url}/papers/{paper_id}/questions", headers=headers)
                    print(f"获取题目状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        questions = data.get("questions", [])
                        print(f"✓ 题目获取成功，数量: {len(questions)}")
                        
                        if questions:
                            print("\n第一个题目的数据结构:")
                            first_question = questions[0]
                            print(json.dumps(first_question, ensure_ascii=False, indent=2))
                            
                            # 检查选项格式
                            options = first_question.get("options", [])
                            scores = first_question.get("scores", [])
                            print(f"\n选项数量: {len(options)}")
                            print(f"分数数量: {len(scores)}")
                            
                            if options:
                                print("选项内容:")
                                for i, option in enumerate(options):
                                    print(f"  {i}: {option}")
                            
                            if scores:
                                print("分数内容:")
                                for i, score in enumerate(scores):
                                    print(f"  {i}: {score}")
                        else:
                            print("✗ 没有题目")
                    else:
                        print(f"✗ 获取题目失败: {response.text}")
                else:
                    print("✗ 没有试卷分配")
            else:
                print(f"✗ 获取试卷分配失败: {response.text}")
                
        else:
            print(f"✗ 登录失败: {response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")

if __name__ == "__main__":
    test_paper_questions() 