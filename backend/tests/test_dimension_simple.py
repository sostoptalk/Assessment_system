import requests
import json

# 测试维度API
try:
    # 创建维度
    data = {
        "paper_id": 5,
        "parent_id": None,
        "name": "测试维度",
        "description": "测试描述",
        "weight": 1.0,
        "order_num": 1
    }
    
    response = requests.post(
        "http://localhost:8000/dimensions/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        dimension = response.json()
        print(f"成功创建维度: {dimension['name']}")
        
        # 获取试卷维度
        response2 = requests.get(f"http://localhost:8000/dimensions/paper/5")
        print(f"获取维度状态码: {response2.status_code}")
        print(f"获取维度响应: {response2.text}")
        
except Exception as e:
    print(f"错误: {e}") 