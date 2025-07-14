import requests
import json

def test_api_detailed():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("详细API测试 - 诊断422错误")
    print("=" * 60)
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ 登录成功，获取到token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. 测试获取试卷列表
            print("\n2. 测试获取试卷列表...")
            response = requests.get(f"{base_url}/papers", headers=headers)
            print(f"获取试卷列表状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                papers = response.json()
                print(f"✅ 获取试卷列表成功，共 {len(papers)} 份试卷")
                if papers:
                    paper_id = papers[0]['id']
                    print(f"   第一个试卷: {papers[0]['name']} (ID: {paper_id})")
                    
                    # 3. 测试按试卷查看结果
                    print(f"\n3. 测试按试卷查看结果 (试卷ID: {paper_id})...")
                    print(f"请求URL: {base_url}/results/by-paper?paper_id={paper_id}")
                    print(f"请求头: {headers}")
                    
                    response = requests.get(f"{base_url}/results/by-paper", params={"paper_id": paper_id}, headers=headers)
                    print(f"按试卷查看结果状态码: {response.status_code}")
                    print(f"响应头: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        results = response.json()
                        print(f"✅ 按试卷查看结果成功，共 {len(results)} 个结果")
                        if results:
                            print(f"   第一个结果: {json.dumps(results[0], indent=2, ensure_ascii=False)}")
                    elif response.status_code == 422:
                        print(f"❌ 422错误 - 参数验证失败")
                        print(f"错误详情: {response.text}")
                    else:
                        print(f"❌ 其他错误: {response.text}")
                else:
                    print("❌ 没有试卷数据")
            else:
                print(f"❌ 获取试卷列表失败: {response.text}")
            
            # 4. 测试获取用户列表
            print("\n4. 测试获取用户列表...")
            response = requests.get(f"{base_url}/users", headers=headers)
            print(f"获取用户列表状态码: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                participants = [u for u in users if u["role"] == "participant"]
                print(f"✅ 获取用户列表成功，共 {len(users)} 个用户，其中被试者 {len(participants)} 个")
                if participants:
                    user_id = participants[0]['id']
                    print(f"   第一个被试者: {participants[0]['real_name']} (ID: {user_id})")
                    
                    # 5. 测试按被试者查看结果
                    print(f"\n5. 测试按被试者查看结果 (用户ID: {user_id})...")
                    print(f"请求URL: {base_url}/results/by-user?user_id={user_id}")
                    print(f"请求头: {headers}")
                    
                    response = requests.get(f"{base_url}/results/by-user", params={"user_id": user_id}, headers=headers)
                    print(f"按被试者查看结果状态码: {response.status_code}")
                    print(f"响应头: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        results = response.json()
                        print(f"✅ 按被试者查看结果成功，共 {len(results)} 个结果")
                        if results:
                            print(f"   第一个结果: {json.dumps(results[0], indent=2, ensure_ascii=False)}")
                    elif response.status_code == 422:
                        print(f"❌ 422错误 - 参数验证失败")
                        print(f"错误详情: {response.text}")
                    else:
                        print(f"❌ 其他错误: {response.text}")
                else:
                    print("❌ 没有被试者数据")
            else:
                print(f"❌ 获取用户列表失败: {response.text}")
        
        else:
            print(f"❌ 登录失败: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_detailed() 