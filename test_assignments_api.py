import requests
import json

BASE_URL = "http://localhost:8000"

def test_assignments_api():
    print("=== 测试分配情况API ===")
    
    # 1. 获取试卷列表
    print("\n1. 获取试卷列表")
    response = requests.get(f"{BASE_URL}/papers")
    if response.status_code == 200:
        papers = response.json()
        if papers:
            paper_id = papers[0]['id']
            print(f"✅ 获取试卷列表成功，使用第一个试卷ID: {paper_id}")
        else:
            print("❌ 没有试卷")
            return
    else:
        print(f"❌ 获取试卷列表失败: {response.status_code}")
        return
    
    # 2. 测试分配情况API
    print(f"\n2. 测试分配情况API: /papers/{paper_id}/list-assignment")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ 获取分配情况成功，共 {len(assignments)} 条记录")
        for assignment in assignments:
            print(f"   - {assignment['user_name']}: {assignment['status']}")
    else:
        print(f"❌ 获取分配情况失败: {response.text}")
    
    # 3. 测试带斜杠的URL
    print(f"\n3. 测试带斜杠的URL: /papers/{paper_id}/list-assignment/")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment/")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        assignments = response.json()
        print(f"✅ 获取分配情况成功，共 {len(assignments)} 条记录")
    else:
        print(f"❌ 获取分配情况失败: {response.text}")

if __name__ == "__main__":
    test_assignments_api() 