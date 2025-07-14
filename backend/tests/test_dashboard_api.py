#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘API
"""
import requests
import json

# 基础URL
base_url = "http://localhost:8000"

def test_dashboard_apis():
    """测试管理员仪表板相关API"""
    
    print("=== 测试管理员仪表板API ===")
    
    # 1. 测试获取统计数据
    print("\n1. 测试获取统计数据...")
    try:
        response = requests.get(f"{base_url}/dashboard/stats")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"统计数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试获取最近测评数据
    print("\n2. 测试获取最近测评数据...")
    try:
        response = requests.get(f"{base_url}/dashboard/recent-assessments?limit=5")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"最近测评数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_dashboard_apis() 