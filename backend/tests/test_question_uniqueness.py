import requests
import json

def test_question_uniqueness():
    base_url = "http://localhost:8000"
    
    print("=== 测试题目匹配唯一性 ===")
    
    # 1. 获取试卷和维度
    print("\n1. 获取试卷和维度...")
    response = requests.get(f"{base_url}/papers/")
    if response.status_code != 200:
        print("获取试卷失败")
        return
    
    papers = response.json()
    if not papers:
        print("没有试卷")
        return
    
    paper_id = papers[0]['id']
    print(f"使用试卷ID: {paper_id}")
    
    # 获取维度
    response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
    if response.status_code != 200:
        print("获取维度失败")
        return
    
    dimensions = response.json()
    if not dimensions:
        print("没有维度")
        return
    
    # 找到第一个有子维度的父维度
    parent_dimension = None
    child_dimension = None
    
    for dim in dimensions:
        if dim.get('children') and len(dim['children']) > 0:
            parent_dimension = dim
            child_dimension = dim['children'][0]
            break
    
    if not child_dimension:
        print("没有找到子维度")
        return
    
    print(f"使用子维度: {child_dimension['name']} (ID: {child_dimension['id']})")
    
    # 2. 获取可匹配题目
    print("\n2. 获取可匹配题目...")
    response = requests.get(f"{base_url}/dimensions/{child_dimension['id']}/available-questions?paper_id={paper_id}")
    if response.status_code != 200:
        print("获取可匹配题目失败")
        return
    
    available_questions = response.json()
    print(f"可匹配题目数: {len(available_questions)}")
    
    if len(available_questions) < 2:
        print("可匹配题目不足，无法测试")
        return
    
    # 3. 匹配第一个题目
    print("\n3. 匹配第一个题目...")
    first_question_id = available_questions[0]['id']
    match_data = {"question_ids": [first_question_id]}
    
    response = requests.post(
        f"{base_url}/dimensions/{child_dimension['id']}/match-questions",
        headers={"Content-Type": "application/json"},
        data=json.dumps(match_data)
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"匹配成功: {result['msg']}")
    else:
        error_data = response.json()
        print(f"匹配失败: {error_data.get('detail', '未知错误')}")
        return
    
    # 4. 验证匹配后的可匹配题目
    print("\n4. 验证匹配后的可匹配题目...")
    response = requests.get(f"{base_url}/dimensions/{child_dimension['id']}/available-questions?paper_id={paper_id}")
    if response.status_code == 200:
        remaining_questions = response.json()
        print(f"匹配后剩余可匹配题目数: {len(remaining_questions)}")
        print(f"减少了 {len(available_questions) - len(remaining_questions)} 道题目")
        
        # 检查已匹配的题目是否还在列表中
        matched_question_still_available = any(q['id'] == first_question_id for q in remaining_questions)
        print(f"已匹配题目仍在可匹配列表中: {matched_question_still_available}")
        
        if matched_question_still_available:
            print("❌ 问题：已匹配的题目仍然出现在可匹配列表中")
        else:
            print("✅ 正确：已匹配的题目已从可匹配列表中移除")
    
    # 5. 测试其他子维度的可匹配题目
    print("\n5. 测试其他子维度的可匹配题目...")
    for child in parent_dimension['children'][1:]:  # 跳过第一个子维度
        print(f"\n测试子维度: {child['name']} (ID: {child['id']})")
        
        response = requests.get(f"{base_url}/dimensions/{child['id']}/available-questions?paper_id={paper_id}")
        if response.status_code == 200:
            questions = response.json()
            print(f"  可匹配题目数: {len(questions)}")
            
            # 检查已匹配的题目是否出现在其他维度的列表中
            matched_question_in_other_dimension = any(q['id'] == first_question_id for q in questions)
            print(f"  已匹配题目出现在此维度列表中: {matched_question_in_other_dimension}")
            
            if matched_question_in_other_dimension:
                print("  ❌ 问题：已匹配的题目仍然出现在其他维度的可匹配列表中")
            else:
                print("  ✅ 正确：已匹配的题目已从其他维度的可匹配列表中移除")
        else:
            print(f"  获取可匹配题目失败: {response.status_code}")

if __name__ == "__main__":
    test_question_uniqueness() 