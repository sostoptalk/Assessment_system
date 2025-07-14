import requests
import json

def test_delete_paper():
    base_url = "http://localhost:8000"
    
    print("=== 测试删除试卷功能 ===")
    
    # 1. 获取试卷列表
    print("\n1. 获取试卷列表...")
    response = requests.get(f"{base_url}/papers/")
    if response.status_code != 200:
        print("获取试卷列表失败")
        return
    
    papers = response.json()
    if not papers:
        print("没有试卷可测试")
        return
    
    print(f"找到 {len(papers)} 个试卷")
    for paper in papers:
        print(f"  - {paper['name']} (ID: {paper['id']})")
    
    # 2. 选择一个试卷进行删除测试
    test_paper = papers[0]
    paper_id = test_paper['id']
    print(f"\n2. 测试删除试卷ID: {paper_id}")
    print(f"试卷名称: {test_paper['name']}")
    
    # 3. 检查试卷的相关数据
    print("\n3. 检查试卷相关数据...")
    
    # 检查试卷题目
    response = requests.get(f"{base_url}/papers/{paper_id}/questions/")
    if response.status_code == 200:
        questions_data = response.json()
        questions = questions_data.get('questions', [])
        print(f"  试卷题目数: {len(questions)}")
    
    # 检查试卷维度
    response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
    if response.status_code == 200:
        dimensions = response.json()
        print(f"  试卷维度数: {len(dimensions)}")
        for dim in dimensions:
            print(f"    - {dim['name']} (ID: {dim['id']})")
            if dim.get('children'):
                for child in dim['children']:
                    print(f"      └─ {child['name']} (ID: {child['id']})")
    
    # 4. 记录删除前的数据
    original_paper_count = len(papers)
    print(f"\n4. 删除前试卷总数: {original_paper_count}")
    
    # 5. 尝试删除试卷
    print(f"\n5. 尝试删除试卷ID: {paper_id}...")
    response = requests.delete(f"{base_url}/papers/{paper_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 删除成功: {result['msg']}")
        
        # 6. 验证试卷已被删除
        print("\n6. 验证试卷已被删除...")
        
        # 重新获取试卷列表
        response = requests.get(f"{base_url}/papers/")
        if response.status_code == 200:
            papers_after = response.json()
            new_count = len(papers_after)
            print(f"删除后试卷总数: {new_count}")
            print(f"减少了 {original_paper_count - new_count} 个试卷")
            
            # 检查特定试卷是否还存在
            paper_still_exists = any(p['id'] == paper_id for p in papers_after)
            if not paper_still_exists:
                print("✅ 试卷已成功删除")
                
                # 验证相关数据也被删除
                print("\n7. 验证相关数据也被删除...")
                
                # 检查维度是否被删除
                response = requests.get(f"{base_url}/dimensions/paper/{paper_id}")
                if response.status_code == 404:
                    print("✅ 试卷维度已删除")
                elif response.status_code == 200:
                    dimensions = response.json()
                    if len(dimensions) == 0:
                        print("✅ 试卷维度已删除（空列表）")
                    else:
                        print(f"❌ 试卷维度仍然存在，数量: {len(dimensions)}")
                else:
                    print(f"❌ 检查维度状态失败，状态码: {response.status_code}")
                
                # 检查试卷题目是否被删除
                response = requests.get(f"{base_url}/papers/{paper_id}/questions/")
                if response.status_code == 404:
                    print("✅ 试卷题目关联已删除")
                elif response.status_code == 200:
                    questions_data = response.json()
                    questions = questions_data.get('questions', [])
                    if len(questions) == 0:
                        print("✅ 试卷题目关联已删除（空列表）")
                    else:
                        print(f"❌ 试卷题目关联仍然存在，数量: {len(questions)}")
                else:
                    print(f"❌ 检查试卷题目状态失败，状态码: {response.status_code}")
                    
            else:
                print("❌ 试卷仍然存在")
        else:
            print("❌ 无法获取删除后的试卷列表")
            
    elif response.status_code == 404:
        print("❌ 试卷不存在")
    elif response.status_code == 500:
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(f"❌ 删除失败: {error_data}")
    else:
        print(f"❌ 删除失败，状态码: {response.status_code}")

if __name__ == "__main__":
    test_delete_paper() 