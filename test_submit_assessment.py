import requests
import json

def test_submit_assessment():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试提交答案功能")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "user1",
        "password": "user123"
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. 获取试卷分配
            print("\n2. 获取试卷分配...")
            response = requests.get(f"{base_url}/my-assignments", headers=headers)
            print(f"获取试卷分配状态码: {response.status_code}")
            
            if response.status_code == 200:
                assignments = response.json()
                print(f"✅ 获取试卷分配成功，共 {len(assignments)} 个分配")
                
                # 找到未完成的分配
                available_assignment = None
                for assignment in assignments:
                    print(f"   分配ID: {assignment['id']}, 状态: {assignment['status']}")
                    if assignment['status'] == 'assigned':
                        available_assignment = assignment
                        break
                
                if available_assignment:
                    assignment_id = available_assignment['id']
                    print(f"   使用未完成的分配ID: {assignment_id}")
                    
                    # 3. 开始测试
                    print(f"\n3. 开始测试 (分配ID: {assignment_id})...")
                    response = requests.post(f"{base_url}/start-assessment/{assignment_id}", headers=headers)
                    print(f"开始测试状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        start_data = response.json()
                        print(f"✅ 开始测试成功")
                        print(f"   试卷名称: {start_data.get('paper_name')}")
                        print(f"   题目数量: {len(start_data.get('questions', []))}")
                        
                        # 4. 提交答案
                        print(f"\n4. 提交答案 (分配ID: {assignment_id})...")
                        
                        # 模拟答案数据
                        questions = start_data.get('questions', [])
                        answers = {}
                        for question in questions[:3]:  # 只答前3题
                            question_id = question['id']
                            if question['type'] == 'single':
                                answers[str(question_id)] = ["A"]  # 单选选A
                            else:
                                answers[str(question_id)] = ["A", "B"]  # 多选选A、B
                        
                        submit_data = {"answers": answers}
                        print(f"提交的答案数据: {json.dumps(submit_data, ensure_ascii=False, indent=2)}")
                        
                        response = requests.post(
                            f"{base_url}/submit-assessment/{assignment_id}",
                            headers={**headers, "Content-Type": "application/json"},
                            json=submit_data
                        )
                        print(f"提交答案状态码: {response.status_code}")
                        
                        if response.status_code == 200:
                            submit_result = response.json()
                            print(f"✅ 提交答案成功")
                            print(f"   消息: {submit_result.get('msg')}")
                            print(f"   完成时间: {submit_result.get('completed_at')}")
                        else:
                            error_data = response.json()
                            print(f"❌ 提交答案失败: {error_data}")
                    else:
                        error_data = response.json()
                        print(f"❌ 开始测试失败: {error_data}")
                else:
                    print("❌ 没有找到未完成的试卷分配")
                    print("   所有分配都已完成，需要管理员重新分配试卷")
            else:
                error_data = response.json()
                print(f"❌ 获取试卷分配失败: {error_data}")
        else:
            error_data = response.json()
            print(f"❌ 登录失败: {error_data}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_submit_assessment() 