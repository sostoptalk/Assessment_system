import requests
import json

BASE_URL = "http://localhost:8000"

def test_assignments_direct():
    print("=== 直接测试分配情况API ===")
    
    # 使用已知的试卷ID
    paper_id = 10
    
    print(f"\n测试试卷ID: {paper_id}")
    
    # 1. 先测试试卷是否存在
    print("\n1. 测试试卷是否存在")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        paper = response.json()
        print(f"✅ 试卷存在: {paper['name']}")
    else:
        print(f"❌ 试卷不存在: {response.text}")
        return
    
    # 2. 测试分配情况API
    print(f"\n2. 测试分配情况API")
    print(f"URL: {BASE_URL}/papers/{paper_id}/list-assignment")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    # 3. 测试带斜杠的URL
    print(f"\n3. 测试带斜杠的URL")
    print(f"URL: {BASE_URL}/papers/{paper_id}/list-assignment/")
    response = requests.get(f"{BASE_URL}/papers/{paper_id}/list-assignment/")
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")

if __name__ == "__main__":
    test_assignments_direct() 