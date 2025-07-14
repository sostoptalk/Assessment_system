import requests
import json

BASE_URL = "http://localhost:8000"

def test_paper_assignment():
    print("=== 测试试卷分配和发布功能 ===")
    
    # 1. 创建试卷
    print("\n1. 创建试卷")
    paper_data = {
        "name": "测试分配功能试卷",
        "description": "用于测试分配和发布功能",
        "duration": 30
    }
    
    response = requests.post(f"{BASE_URL}/papers", json=paper_data)
    if response.status_code == 200:
        paper = response.json()
        paper_id = paper["id"]
        print(f"✅ 试卷创建成功，ID: {paper_id}")
        print(f"   名称: {paper['name']}")
        print(f"   状态: {paper['status']}")
    else:
        print(f"❌ 试卷创建失败: {response.status_code}")
        return
    
    # 2. 获取用户列表
    print("\n2. 获取用户列表")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code == 200:
        users = response.json()
        participants = [u for u in users if u['role'] == 'participant']
        print(f"✅ 获取用户列表成功，共 {len(participants)} 个被试者")
        for user in participants:
            print(f"   - {user['real_name']} ({user['username']})")
    else:
        print(f"❌ 获取用户列表失败: {response.status_code}")
        return
    
    # 3. 测试分配功能
    print(f"\n3. 测试分配功能")
    if participants:
        user_ids = [participants[0]['id']]  # 只分配给第一个被试者
        assign_data = {"user_ids": user_ids}
        
        response = requests.post(f"{BASE_URL}/papers/{paper_id}/assign", json=assign_data)
        if response.status_code == 200:
            print("✅ 分配成功")
        else:
            print(f"❌ 分配失败: {response.status_code}")
    
    # 4. 查看分配情况
    print(f"\n4. 查看分配情况")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment")
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ 获取分配情况成功，共 {len(assignments)} 条分配记录")
        for assignment in assignments:
            print(f"   - {assignment['user_name']}: {assignment['status']}")
    else:
        print(f"❌ 获取分配情况失败: {response.status_code}")
    
    # 5. 测试发布功能（会分配给所有被试者）
    print(f"\n5. 测试发布功能")
    response = requests.post(f"{BASE_URL}/papers/{paper_id}/publish")
    if response.status_code == 200:
        print("✅ 发布成功")
    else:
        print(f"❌ 发布失败: {response.status_code}")
    
    # 6. 再次查看分配情况
    print(f"\n6. 发布后查看分配情况")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment")
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ 获取分配情况成功，共 {len(assignments)} 条分配记录")
        for assignment in assignments:
            print(f"   - {assignment['user_name']}: {assignment['status']}")
    else:
        print(f"❌ 获取分配情况失败: {response.status_code}")
    
    # 7. 测试重新分配功能
    print(f"\n7. 测试重新分配功能")
    if participants:
        user_ids = [participants[0]['id']]
        assign_data = {"user_ids": user_ids}
        
        response = requests.post(f"{BASE_URL}/papers/{paper_id}/assign", json=assign_data)
        if response.status_code == 200:
            print("✅ 重新分配成功")
        else:
            print(f"❌ 重新分配失败: {response.status_code}")

if __name__ == "__main__":
    test_paper_assignment() 