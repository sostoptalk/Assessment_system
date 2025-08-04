import os
import sys
import time
import json
import requests
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 定义API基础URL
BASE_URL = "http://localhost:3000"  # 修改为实际的API地址

# 测试账号
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def get_auth_token():
    """获取认证令牌"""
    try:
        response = requests.post(f"{BASE_URL}/login", data=TEST_CREDENTIALS)
        response.raise_for_status()  # 如果请求失败，会抛出异常
        token = response.json().get("access_token")
        if not token:
            print("❌ 登录失败：未获取到令牌")
            return None
        return token
    except Exception as e:
        print(f"❌ 登录失败：{str(e)}")
        return None

def test_batch_generate_report():
    """测试批量生成报告"""
    print("=== 测试批量生成报告 ===")
    
    token = get_auth_token()
    if not token:
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 测试试卷分配情况
    try:
        print("1. 获取试卷10的分配情况...")
        response = requests.get(f"{BASE_URL}/papers/10/list-assignment", headers=headers)
        response.raise_for_status()
        assignments = response.json()
        print(f"✅ 获取到 {len(assignments)} 条分配记录")
        
        # 查找用户6的完成记录
        user6_assignment = None
        for assignment in assignments:
            if assignment.get('user_id') == 6 and assignment.get('status') == 'completed':
                user6_assignment = assignment
                break
        
        if user6_assignment:
            print(f"✅ 用户6完成了试卷10，分配ID: {user6_assignment.get('id')}")
        else:
            print("❌ 未找到用户6完成试卷10的记录")
            return False
            
    except Exception as e:
        print(f"❌ 获取试卷分配失败：{str(e)}")
        return False
    
    # 2. 批量生成报告
    try:
        print("\n2. 批量生成报告...")
        payload = {
            "paper_id": 10,
            "user_ids": [6]  # 只测试用户6
        }
        response = requests.post(f"{BASE_URL}/reports/batch-generate", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success") and result.get("task_ids"):
            task_ids = result.get("task_ids")
            print(f"✅ 成功提交报告生成任务，任务ID: {task_ids}")
        else:
            print(f"❌ 提交报告生成任务失败: {result}")
            return False
            
        # 3. 轮询任务状态
        print("\n3. 轮询任务状态...")
        max_tries = 10
        for i in range(max_tries):
            print(f"   轮询 {i+1}/{max_tries}...")
            try:
                # 构建查询参数
                params = {"task_ids[]": task_ids}
                response = requests.get(f"{BASE_URL}/reports/status", headers=headers, params=params)
                response.raise_for_status()
                status_data = response.json()
                
                print(f"   状态响应: {json.dumps(status_data, indent=2)}")
                
                # 检查所有任务是否完成
                all_completed = True
                for task_id, task_status in status_data.items():
                    if task_status.get("status") not in ["completed", "failed"]:
                        all_completed = False
                        break
                        
                if all_completed:
                    print("✅ 所有任务已完成")
                    return True
                    
                # 等待一会再查询
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 查询任务状态失败: {str(e)}")
                time.sleep(2)
                
        print("❌ 超过最大等待时间，任务未完成")
        return False
            
    except Exception as e:
        print(f"❌ 批量生成报告失败：{str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    print(f"开始测试时间: {datetime.now()}")
    success = test_batch_generate_report()
    if success:
        print("\n✅ 测试通过！")
    else:
        print("\n❌ 测试失败！")
    print(f"结束测试时间: {datetime.now()}") 