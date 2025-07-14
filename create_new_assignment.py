import requests
import json

def create_new_assignment():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("创建新的试卷分配")
    print("=" * 60)
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ 管理员登录成功，获取到token: {token[:20]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. 获取试卷列表
            print("\n2. 获取试卷列表...")
            response = requests.get(f"{base_url}/papers", headers=headers)
            print(f"获取试卷列表状态码: {response.status_code}")
            
            if response.status_code == 200:
                papers = response.json()
                print(f"✅ 获取试卷列表成功，共 {len(papers)} 份试卷")
                
                if papers:
                    paper = papers[0]  # 使用第一份试卷
                    paper_id = paper['id']
                    print(f"   使用试卷: {paper['name']} (ID: {paper_id})")
                    
                    # 3. 获取用户列表
                    print("\n3. 获取用户列表...")
                    response = requests.get(f"{base_url}/users", headers=headers)
                    print(f"获取用户列表状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        users = response.json()
                        participants = [u for u in users if u['role'] == 'participant']
                        print(f"✅ 获取用户列表成功，共 {len(participants)} 个被试者")
                        
                        if participants:
                            # 选择第一个被试者
                            participant = participants[0]
                            user_id = participant['id']
                            print(f"   给被试者分配: {participant['real_name']} ({participant['username']}) (ID: {user_id})")
                            
                            # 4. 分配试卷
                            print(f"\n4. 分配试卷...")
                            assign_data = {"user_ids": [user_id]}
                            
                            response = requests.post(
                                f"{base_url}/papers/{paper_id}/assign",
                                headers={**headers, "Content-Type": "application/json"},
                                json=assign_data
                            )
                            print(f"分配试卷状态码: {response.status_code}")
                            
                            if response.status_code == 200:
                                result = response.json()
                                print(f"✅ 试卷分配成功")
                                print(f"   消息: {result.get('msg')}")
                                
                                # 5. 验证分配
                                print(f"\n5. 验证分配...")
                                response = requests.get(f"{base_url}/users", headers=headers)
                                if response.status_code == 200:
                                    users = response.json()
                                    for user in users:
                                        if user['id'] == user_id:
                                            print(f"   用户: {user['real_name']} ({user['username']})")
                                            break
                            else:
                                error_data = response.json()
                                print(f"❌ 试卷分配失败: {error_data}")
                        else:
                            print("❌ 没有找到被试者")
                    else:
                        error_data = response.json()
                        print(f"❌ 获取用户列表失败: {error_data}")
                else:
                    print("❌ 没有找到试卷")
            else:
                error_data = response.json()
                print(f"❌ 获取试卷列表失败: {error_data}")
        else:
            error_data = response.json()
            print(f"❌ 管理员登录失败: {error_data}")
            
    except Exception as e:
        print(f"❌ 创建分配过程中出现错误: {str(e)}")

if __name__ == "__main__":
    create_new_assignment() 