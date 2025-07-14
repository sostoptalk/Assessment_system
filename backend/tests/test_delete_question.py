import requests
import json

def test_delete_question():
    base_url = "http://localhost:8000"
    
    print("=== 测试删除题目功能 ===")
    
    # 1. 获取题目列表
    print("\n1. 获取题目列表...")
    response = requests.get(f"{base_url}/questions/")
    if response.status_code != 200:
        print("获取题目列表失败")
        return
    
    questions = response.json()
    if not questions:
        print("没有题目可测试")
        return
    
    print(f"找到 {len(questions)} 道题目")
    
    # 2. 选择一个题目进行删除测试
    test_question = questions[0]
    question_id = test_question['id']
    print(f"\n2. 测试删除题目ID: {question_id}")
    print(f"题目内容: {test_question['content'][:50]}...")
    
    # 3. 检查该题目是否在试卷中使用
    print("\n3. 检查题目是否在试卷中使用...")
    response = requests.get(f"{base_url}/papers/")
    if response.status_code == 200:
        papers = response.json()
        for paper in papers:
            response = requests.get(f"{base_url}/papers/{paper['id']}/questions/")
            if response.status_code == 200:
                paper_questions = response.json().get('questions', [])
                for pq in paper_questions:
                    if pq['id'] == question_id:
                        print(f"  题目在试卷 '{paper['name']}' 中使用")
                        break
    
    # 4. 记录删除前的题目数量
    original_count = len(questions)
    print(f"\n4. 删除前题目总数: {original_count}")
    
    # 5. 尝试删除题目
    print(f"\n5. 尝试删除题目ID: {question_id}...")
    response = requests.delete(f"{base_url}/questions/{question_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 删除成功: {result['msg']}")
        
        # 6. 验证题目已被删除
        print("\n6. 验证题目已被删除...")
        
        # 重新获取题目列表
        response = requests.get(f"{base_url}/questions/")
        if response.status_code == 200:
            questions_after = response.json()
            new_count = len(questions_after)
            print(f"删除后题目总数: {new_count}")
            print(f"减少了 {original_count - new_count} 道题目")
            
            # 检查特定题目是否还存在
            question_still_exists = any(q['id'] == question_id for q in questions_after)
            if not question_still_exists:
                print("✅ 题目已成功删除")
            else:
                print("❌ 题目仍然存在")
        else:
            print("❌ 无法获取删除后的题目列表")
            
    elif response.status_code == 404:
        print("❌ 题目不存在")
    elif response.status_code == 500:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(f"❌ 删除失败: {error_data}")
    else:
        print(f"❌ 删除失败，状态码: {response.status_code}")

if __name__ == "__main__":
    test_delete_question() 