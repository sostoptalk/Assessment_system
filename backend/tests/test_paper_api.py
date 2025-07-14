import requests
import json

BASE_URL = "http://localhost:8000"

def test_paper_api():
    print("=== 测试试卷管理API ===")
    
    # 1. 创建试卷
    print("\n1. 创建试卷")
    paper_data = {
        "name": "商业推理能力测评试卷",
        "description": "用于评估被试者的商业推理能力",
        "duration": 60
    }
    
    response = requests.post(f"{BASE_URL}/papers", json=paper_data)
    if response.status_code == 200:
        paper = response.json()
        paper_id = paper["id"]
        print(f"✅ 试卷创建成功，ID: {paper_id}")
        print(f"   名称: {paper['name']}")
        print(f"   时长: {paper['duration']}分钟")
        print(f"   状态: {paper['status']}")
    else:
        print(f"❌ 试卷创建失败: {response.status_code}")
        return
    
    # 2. 获取试卷列表
    print("\n2. 获取试卷列表")
    response = requests.get(f"{BASE_URL}/papers")
    if response.status_code == 200:
        papers = response.json()
        print(f"✅ 获取试卷列表成功，共 {len(papers)} 份试卷")
        for paper in papers:
            print(f"   - {paper['name']} (ID: {paper['id']}, 状态: {paper['status']})")
    else:
        print(f"❌ 获取试卷列表失败: {response.status_code}")
    
    # 3. 发布试卷
    print(f"\n3. 发布试卷 (ID: {paper_id})")
    response = requests.post(f"{BASE_URL}/papers/{paper_id}/publish")
    if response.status_code == 200:
        print("✅ 试卷发布成功")
    else:
        print(f"❌ 试卷发布失败: {response.status_code}")
    
    # 4. 获取用户列表（用于分配）
    print("\n4. 获取用户列表")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        users = response.json()
        participant_users = [u for u in users if u["role"] == "participant"]
        print(f"✅ 获取用户列表成功，共 {len(users)} 个用户，其中被试者 {len(participant_users)} 个")
        if participant_users:
            user_ids = [u["id"] for u in participant_users[:2]]  # 选择前2个被试者
            print(f"   选择用户ID: {user_ids}")
            
            # 5. 分配试卷给用户
            print(f"\n5. 分配试卷给用户 (试卷ID: {paper_id}, 用户ID: {user_ids})")
            assign_data = {"user_ids": user_ids}
            response = requests.post(f"{BASE_URL}/papers/{paper_id}/assign", json=assign_data)
            if response.status_code == 200:
                print("✅ 试卷分配成功")
            else:
                print(f"❌ 试卷分配失败: {response.status_code}")
    else:
        print(f"❌ 获取用户列表失败: {response.status_code}")
    
    # 6. 获取题目列表（用于添加题目到试卷）
    print("\n6. 获取题目列表")
    response = requests.get(f"{BASE_URL}/questions")
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ 获取题目列表成功，共 {len(questions)} 道题目")
        if questions:
            question_ids = [q["id"] for q in questions[:3]]  # 选择前3道题目
            print(f"   选择题目ID: {question_ids}")
            
            # 7. 添加题目到试卷
            print(f"\n7. 添加题目到试卷 (试卷ID: {paper_id}, 题目ID: {question_ids})")
            response = requests.post(f"{BASE_URL}/papers/{paper_id}/questions", json=question_ids)
            if response.status_code == 200:
                print("✅ 题目添加成功")
            else:
                print(f"❌ 题目添加失败: {response.status_code}")
            
            # 8. 获取试卷题目
            print(f"\n8. 获取试卷题目 (试卷ID: {paper_id})")
            response = requests.get(f"{BASE_URL}/papers/{paper_id}/questions")
            if response.status_code == 200:
                paper_questions = response.json()
                print(f"✅ 获取试卷题目成功，共 {len(paper_questions['questions'])} 道题目")
                for q in paper_questions['questions']:
                    print(f"   - 题目{q['order_num']}: {q['content'][:50]}...")
            else:
                print(f"❌ 获取试卷题目失败: {response.status_code}")
    else:
        print(f"❌ 获取题目列表失败: {response.status_code}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_paper_api() 