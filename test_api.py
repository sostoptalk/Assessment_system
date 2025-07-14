import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    # 1. 登录获取token
    print("1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/login", data=login_data)
    print(f"登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"✅ 登录成功，获取到token: {token[:20]}...")
        
        # 2. 测试获取试卷列表
        print("\n2. 测试获取试卷列表...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/papers", headers=headers)
        print(f"获取试卷列表状态码: {response.status_code}")
        if response.status_code == 200:
            papers = response.json()
            print(f"✅ 获取试卷列表成功，共 {len(papers)} 份试卷")
            if papers:
                print(f"   第一个试卷: {papers[0]['name']} (ID: {papers[0]['id']})")
        else:
            print(f"❌ 获取试卷列表失败: {response.text}")
        
        # 3. 测试获取用户列表
        print("\n3. 测试获取用户列表...")
        response = requests.get(f"{base_url}/users", headers=headers)
        print(f"获取用户列表状态码: {response.status_code}")
        if response.status_code == 200:
            users = response.json()
            participants = [u for u in users if u["role"] == "participant"]
            print(f"✅ 获取用户列表成功，共 {len(users)} 个用户，其中被试者 {len(participants)} 个")
            if participants:
                print(f"   第一个被试者: {participants[0]['real_name']} (ID: {participants[0]['id']})")
        else:
            print(f"❌ 获取用户列表失败: {response.text}")
        
        # 4. 测试测试结果API
        if papers and participants:
            paper_id = papers[0]['id']
            user_id = participants[0]['id']
            
            print(f"\n4. 测试按试卷查看结果 (试卷ID: {paper_id})...")
            response = requests.get(f"{base_url}/results/by-paper", params={"paper_id": paper_id}, headers=headers)
            print(f"按试卷查看结果状态码: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 按试卷查看结果成功，共 {len(results)} 个结果")
            else:
                print(f"❌ 按试卷查看结果失败: {response.text}")
            
            print(f"\n5. 测试按被试者查看结果 (用户ID: {user_id})...")
            response = requests.get(f"{base_url}/results/by-user", params={"user_id": user_id}, headers=headers)
            print(f"按被试者查看结果状态码: {response.status_code}")
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 按被试者查看结果成功，共 {len(results)} 个结果")
            else:
                print(f"❌ 按被试者查看结果失败: {response.text}")
        
    else:
        print(f"❌ 登录失败: {response.text}")

if __name__ == "__main__":
    test_api() 