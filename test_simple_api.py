import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple_api():
    print("=== 测试基本API ===")
    
    # 1. 测试获取试卷列表
    print("\n1. 测试获取试卷列表")
    response = requests.get(f"{BASE_URL}/papers")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        papers = response.json()
        print(f"✅ 获取试卷列表成功，共 {len(papers)} 份试卷")
        if papers:
            print(f"   第一个试卷: {papers[0]['name']} (ID: {papers[0]['id']})")
    else:
        print(f"❌ 获取试卷列表失败: {response.text}")
        return
    
    # 2. 测试获取用户列表
    print("\n2. 测试获取用户列表")
    response = requests.get(f"{BASE_URL}/users")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
    else:
        print(f"❌ 获取用户列表失败: {response.text}")
    
    # 3. 测试获取题目列表
    print("\n3. 测试获取题目列表")
    response = requests.get(f"{BASE_URL}/questions")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ 获取题目列表成功，共 {len(questions)} 道题目")
    else:
        print(f"❌ 获取题目列表失败: {response.text}")

if __name__ == "__main__":
    test_simple_api() 