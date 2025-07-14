#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试被试者测试相关API
"""
import requests
import json

def test_assessment_api():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("被试者测试API测试")
    print("=" * 60)
    
    # 1. 测试获取试卷分配
    print("\n1. 测试获取试卷分配...")
    try:
        response = requests.get(f"{base_url}/my-assignments")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✓ 试卷分配获取成功")
            print(f"  - 分配数量: {len(data)}")
            for assignment in data:
                print(f"    * {assignment['paper_name']} - 状态: {assignment['status']}")
        else:
            print(f"✗ 获取试卷分配失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("注意: 开始测试和提交答案API需要登录Token，请在浏览器中测试")

if __name__ == "__main__":
    test_assessment_api() 