import requests
import json

# 基础URL
base_url = "http://localhost:8000"

def debug_api_errors():
    """调试API错误"""
    
    print("=== 调试API错误 ===")
    
    # 1. 测试获取题目
    print("\n1. 测试获取题目...")
    try:
        response = requests.get(f"{base_url}/questions/")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            print(f"题目数量: {len(data)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取统计数据
    print("\n2. 测试获取统计数据...")
    try:
        response = requests.get(f"{base_url}/dashboard/stats")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        if response.status_code == 200:
            data = response.json()
            print(f"统计数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 3. 测试获取维度
    print("\n3. 测试获取维度...")
    try:
        # 先获取试卷
        response = requests.get(f"{base_url}/papers/")
        if response.status_code == 200:
            papers = response.json()
            if papers:
                paper_id = papers[0]["id"]
                print(f"使用试卷ID: {paper_id}")
                
                # 测试获取维度
                response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
                print(f"维度API状态码: {response.status_code}")
                print(f"维度API响应: {response.text}")
            else:
                print("没有可用试卷")
        else:
            print(f"获取试卷失败: {response.text}")
    except Exception as e:
        print(f"测试维度失败: {e}")

if __name__ == "__main__":
    debug_api_errors() 