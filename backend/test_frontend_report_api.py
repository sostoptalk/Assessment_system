import requests
import json
import time

def test_frontend_report_generation():
    """测试前端报告生成API调用"""
    print("开始测试前端报告生成API...")
    
    # 模拟前端调用批量生成报告API
    url = "http://localhost:8000/reports/batch-generate"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }
    
    # 模拟前端传递的数据
    data = {
        "paper_id": 16,  # 商业推理能力测评
        "user_ids": [28, 29]  # 使用实际存在的用户ID: user1, user2
    }
    
    try:
        print(f"发送请求到: {url}")
        print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功: {result}")
            
            if result.get("success") and result.get("task_ids"):
                task_ids = result["task_ids"]
                print(f"任务ID: {task_ids}")
                
                # 轮询任务状态
                for i in range(10):  # 最多轮询10次
                    print(f"\n=== 第{i+1}次轮询任务状态 ===")
                    
                    status_url = "http://localhost:8000/reports/status"
                    status_params = {"task_ids": task_ids}
                    
                    status_response = requests.get(status_url, params=status_params)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"状态数据: {json.dumps(status_data, ensure_ascii=False, indent=2)}")
                        
                        # 检查是否所有任务都完成
                        all_completed = True
                        for task_id, task_status in status_data.items():
                            if task_status["status"] == "completed":
                                print(f"✅ 任务 {task_id} 已完成")
                                if task_status.get("file_path"):
                                    print(f"   文件路径: {task_status['file_path']}")
                            elif task_status["status"] == "failed":
                                print(f"❌ 任务 {task_id} 失败: {task_status.get('error_message', '未知错误')}")
                                all_completed = False
                            elif task_status["status"] in ["pending", "generating"]:
                                print(f"⏳ 任务 {task_id} 进行中: {task_status['status']}")
                                all_completed = False
                        
                        if all_completed:
                            print("\n🎉 所有报告生成任务已完成！")
                            break
                    else:
                        print(f"❌ 获取状态失败: {status_response.status_code}")
                    
                    time.sleep(2)  # 等待2秒后再次轮询
            else:
                print("❌ API返回数据格式不正确")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端服务正在运行在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    test_frontend_report_generation() 