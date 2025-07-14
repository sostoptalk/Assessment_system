import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/login", data={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("登录成功")
        return token
    else:
        print(f"登录失败: {response.text}")
        return None

def test_get_reports(token):
    """测试获取报告列表"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试获取报告列表 ===")
    response = requests.get(f"{BASE_URL}/reports", headers=headers, params={
        "page": 1,
        "page_size": 10
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"报告总数: {data['total']}")
        print(f"当前页: {data['page']}")
        print(f"每页数量: {data['page_size']}")
        print(f"报告列表: {len(data['reports'])} 条")
        
        for report in data['reports']:
            print(f"  - {report['user_name']} - {report['paper_name']} - {report['file_name']}")
        
        return data['reports']
    else:
        print(f"获取报告列表失败: {response.text}")
        return []

def test_batch_generate_reports(token):
    """测试批量生成报告"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== 测试批量生成报告 ===")
    
    # 获取试卷列表
    response = requests.get(f"{BASE_URL}/papers", headers=headers)
    if response.status_code != 200:
        print("获取试卷列表失败")
        return
    
    papers = response.json()
    if not papers:
        print("没有可用的试卷")
        return
    
    paper_id = papers[0]['id']
    print(f"使用试卷: {papers[0]['name']} (ID: {paper_id})")
    
    # 获取用户列表
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    if response.status_code != 200:
        print("获取用户列表失败")
        return
    
    users = [u for u in response.json() if u['role'] == 'participant']
    if not users:
        print("没有可用的被试者")
        return
    
    user_ids = [users[0]['id']]
    print(f"使用被试者: {users[0]['real_name']} (ID: {users[0]['id']})")
    
    # 批量生成报告
    response = requests.post(f"{BASE_URL}/reports/batch-generate", 
                           headers=headers,
                           json={
                               "paper_id": paper_id,
                               "user_ids": user_ids
                           })
    
    if response.status_code == 200:
        data = response.json()
        print(f"批量生成任务已提交，任务ID: {data['task_ids']}")
        
        # 轮询任务状态
        task_ids = data['task_ids']
        for i in range(10):  # 最多等待20秒
            time.sleep(2)
            response = requests.get(f"{BASE_URL}/reports/status", 
                                 headers=headers,
                                 params={"task_ids[]": task_ids})
            
            if response.status_code == 200:
                status_data = response.json()
                all_completed = True
                for task_id in task_ids:
                    if task_id in status_data:
                        status = status_data[task_id]
                        print(f"任务 {task_id}: {status['status']} - {status['progress']}%")
                        if status['status'] not in ['completed', 'failed']:
                            all_completed = False
                
                if all_completed:
                    print("所有任务已完成")
                    break
            else:
                print(f"获取任务状态失败: {response.text}")
    else:
        print(f"批量生成报告失败: {response.text}")

def test_download_report(token, report_id):
    """测试下载报告"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== 测试下载报告 (ID: {report_id}) ===")
    response = requests.get(f"{BASE_URL}/reports/{report_id}/download", headers=headers)
    
    if response.status_code == 200:
        filename = f"downloaded_report_{report_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"报告下载成功: {filename}")
    else:
        print(f"下载报告失败: {response.text}")

def test_delete_report(token, report_id):
    """测试删除报告"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== 测试删除报告 (ID: {report_id}) ===")
    response = requests.delete(f"{BASE_URL}/reports/{report_id}", headers=headers)
    
    if response.status_code == 200:
        print("报告删除成功")
    else:
        print(f"删除报告失败: {response.text}")

def test_batch_delete_reports(token, report_ids):
    """测试批量删除报告"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== 测试批量删除报告 (IDs: {report_ids}) ===")
    response = requests.delete(f"{BASE_URL}/reports/batch", 
                             headers=headers,
                             json={"report_ids": report_ids})
    
    if response.status_code == 200:
        data = response.json()
        print(f"批量删除成功: {data['message']}")
    else:
        print(f"批量删除失败: {response.text}")

def main():
    """主测试函数"""
    print("开始测试报告管理功能...")
    
    # 登录
    token = login()
    if not token:
        return
    
    # 测试获取报告列表
    reports = test_get_reports(token)
    
    # 测试批量生成报告
    test_batch_generate_reports(token)
    
    # 等待一段时间后再次获取报告列表
    print("\n等待5秒后重新获取报告列表...")
    time.sleep(5)
    reports = test_get_reports(token)
    
    # 如果有报告，测试下载和删除功能
    if reports:
        report_id = reports[0]['id']
        
        # 测试下载报告
        test_download_report(token, report_id)
        
        # 测试删除报告
        test_delete_report(token, report_id)
        
        # 再次获取报告列表确认删除
        print("\n删除后重新获取报告列表...")
        reports = test_get_reports(token)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 