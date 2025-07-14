#!/usr/bin/env python3
"""
测试维度API的脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dimension_api():
    """测试维度API"""
    print("开始测试维度API...")
    
    # 1. 获取试卷列表
    print("\n1. 获取试卷列表")
    try:
        response = requests.get(f"{BASE_URL}/papers/")
        if response.status_code == 200:
            papers = response.json()
            print(f"成功获取 {len(papers)} 个试卷")
            if papers:
                paper_id = papers[0]['id']
                print(f"使用试卷ID: {paper_id}")
            else:
                print("没有试卷，无法继续测试")
                return
        else:
            print(f"获取试卷列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"获取试卷列表出错: {e}")
        return
    
    # 2. 创建维度
    print("\n2. 创建维度")
    dimension_data = {
        "paper_id": paper_id,
        "parent_id": None,
        "name": "测试大维度",
        "description": "这是一个测试大维度",
        "weight": 1.0,
        "order_num": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dimensions/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(dimension_data)
        )
        if response.status_code == 200:
            dimension = response.json()
            print(f"成功创建维度: {dimension['name']} (ID: {dimension['id']})")
            parent_dimension_id = dimension['id']
        else:
            print(f"创建维度失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return
    except Exception as e:
        print(f"创建维度出错: {e}")
        return
    
    # 3. 创建子维度
    print("\n3. 创建子维度")
    child_dimension_data = {
        "paper_id": paper_id,
        "parent_id": parent_dimension_id,
        "name": "测试小维度",
        "description": "这是一个测试小维度",
        "weight": 0.5,
        "order_num": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/dimensions/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(child_dimension_data)
        )
        if response.status_code == 200:
            child_dimension = response.json()
            print(f"成功创建子维度: {child_dimension['name']} (ID: {child_dimension['id']})")
        else:
            print(f"创建子维度失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"创建子维度出错: {e}")
    
    # 4. 获取试卷维度
    print("\n4. 获取试卷维度")
    try:
        response = requests.get(f"{BASE_URL}/dimensions/paper/{paper_id}")
        if response.status_code == 200:
            dimensions = response.json()
            print(f"成功获取 {len(dimensions)} 个维度")
            for dim in dimensions:
                print(f"  - {dim['name']} (ID: {dim['id']}, 父ID: {dim.get('parent_id', '无')})")
                if dim.get('children'):
                    for child in dim['children']:
                        print(f"    - {child['name']} (ID: {child['id']})")
        else:
            print(f"获取试卷维度失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"获取试卷维度出错: {e}")
    
    # 5. 更新维度
    print("\n5. 更新维度")
    update_data = {
        "paper_id": paper_id,
        "parent_id": None,
        "name": "更新后的测试大维度",
        "description": "这是更新后的测试大维度",
        "weight": 2.0,
        "order_num": 2
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/dimensions/{parent_dimension_id}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(update_data)
        )
        if response.status_code == 200:
            updated_dimension = response.json()
            print(f"成功更新维度: {updated_dimension['name']}")
        else:
            print(f"更新维度失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"更新维度出错: {e}")
    
    # 6. 删除维度
    print("\n6. 删除维度")
    try:
        response = requests.delete(f"{BASE_URL}/dimensions/{parent_dimension_id}")
        if response.status_code == 200:
            print("成功删除维度")
        else:
            print(f"删除维度失败: {response.status_code}")
            print(f"错误信息: {response.text}")
    except Exception as e:
        print(f"删除维度出错: {e}")
    
    print("\n维度API测试完成!")

if __name__ == "__main__":
    test_dimension_api() 