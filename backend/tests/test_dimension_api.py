import requests
import json

# 基础URL
base_url = "http://localhost:8000"

def test_dimension_apis():
    """测试维度管理相关API"""
    
    print("=== 测试维度管理API ===")
    
    # 1. 创建试卷（如果不存在）
    print("\n1. 创建测试试卷...")
    paper_data = {
        "name": "维度测试试卷",
        "description": "用于测试维度功能的试卷",
        "duration": 60
    }
    
    try:
        response = requests.post(f"{base_url}/papers/", json=paper_data)
        if response.status_code == 200:
            paper = response.json()
            paper_id = paper["id"]
            print(f"试卷创建成功，ID: {paper_id}")
        else:
            # 如果创建失败，尝试获取现有试卷
            response = requests.get(f"{base_url}/papers/")
            if response.status_code == 200:
                papers = response.json()
                if papers:
                    paper_id = papers[0]["id"]
                    print(f"使用现有试卷，ID: {paper_id}")
                else:
                    print("没有可用试卷")
                    return
            else:
                print("获取试卷失败")
                return
    except Exception as e:
        print(f"创建试卷失败: {e}")
        return
    
    # 2. 创建大维度
    print("\n2. 创建大维度...")
    major_dimension_data = {
        "paper_id": paper_id,
        "name": "认知能力",
        "description": "测试被试者的认知能力水平",
        "weight": 0.4,
        "order_num": 1
    }
    
    try:
        response = requests.post(f"{base_url}/dimensions/", json=major_dimension_data)
        if response.status_code == 200:
            major_dimension = response.json()
            major_dimension_id = major_dimension["id"]
            print(f"大维度创建成功，ID: {major_dimension_id}")
        else:
            print(f"创建大维度失败: {response.text}")
            return
    except Exception as e:
        print(f"创建大维度失败: {e}")
        return
    
    # 3. 创建小维度
    print("\n3. 创建小维度...")
    minor_dimension_data = {
        "paper_id": paper_id,
        "parent_id": major_dimension_id,
        "name": "逻辑推理",
        "description": "测试逻辑推理能力",
        "weight": 0.6,
        "order_num": 1
    }
    
    try:
        response = requests.post(f"{base_url}/dimensions/", json=minor_dimension_data)
        if response.status_code == 200:
            minor_dimension = response.json()
            minor_dimension_id = minor_dimension["id"]
            print(f"小维度创建成功，ID: {minor_dimension_id}")
        else:
            print(f"创建小维度失败: {response.text}")
            return
    except Exception as e:
        print(f"创建小维度失败: {e}")
        return
    
    # 4. 获取试卷的所有维度
    print("\n4. 获取试卷的所有维度...")
    try:
        response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
        if response.status_code == 200:
            dimensions = response.json()
            print(f"维度数据: {json.dumps(dimensions, ensure_ascii=False, indent=2)}")
        else:
            print(f"获取维度失败: {response.text}")
    except Exception as e:
        print(f"获取维度失败: {e}")
    
    # 5. 更新维度
    print("\n5. 更新维度...")
    update_data = {
        "name": "认知能力（已更新）",
        "weight": 0.5
    }
    
    try:
        response = requests.put(f"{base_url}/dimensions/{major_dimension_id}", json=update_data)
        if response.status_code == 200:
            updated_dimension = response.json()
            print(f"维度更新成功: {updated_dimension['name']}")
        else:
            print(f"更新维度失败: {response.text}")
    except Exception as e:
        print(f"更新维度失败: {e}")
    
    # 6. 测试添加题目到试卷（带维度）
    print("\n6. 测试添加题目到试卷（带维度）...")
    
    # 首先获取一些题目
    try:
        response = requests.get(f"{base_url}/questions/")
        if response.status_code == 200:
            questions = response.json()
            if questions:
                question_id = questions[0]["id"]
                
                # 添加题目到试卷，指定维度
                question_with_dimension = [{
                    "question_id": question_id,
                    "dimension_id": minor_dimension_id
                }]
                
                response = requests.post(f"{base_url}/papers/{paper_id}/questions", json=question_with_dimension)
                if response.status_code == 200:
                    print("题目添加成功（带维度）")
                else:
                    print(f"添加题目失败: {response.text}")
            else:
                print("没有可用题目")
        else:
            print(f"获取题目失败: {response.text}")
    except Exception as e:
        print(f"测试添加题目失败: {e}")
    
    # 7. 获取试卷题目（验证维度信息）
    print("\n7. 获取试卷题目（验证维度信息）...")
    try:
        response = requests.get(f"{base_url}/papers/{paper_id}/questions")
        if response.status_code == 200:
            paper_questions = response.json()
            print(f"试卷题目: {json.dumps(paper_questions, ensure_ascii=False, indent=2)}")
        else:
            print(f"获取试卷题目失败: {response.text}")
    except Exception as e:
        print(f"获取试卷题目失败: {e}")

if __name__ == "__main__":
    test_dimension_apis() 