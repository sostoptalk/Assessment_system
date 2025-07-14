#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘数据完整性
"""
import requests
import json
from datetime import datetime, timedelta

def test_dashboard_complete():
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("仪表盘数据完整性测试")
    print("=" * 60)
    
    # 1. 测试统计数据API
    print("\n1. 测试统计数据API...")
    try:
        response = requests.get(f"{base_url}/dashboard/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✓ 统计数据获取成功")
            print(f"  - 总被试者数: {stats['total_participants']}")
            print(f"  - 题库题目数: {stats['total_questions']}")
            print(f"  - 已生成报告: {stats['completed_reports']}")
            print(f"  - 平均得分: {stats['avg_score']}")
        else:
            print(f"✗ 统计数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 统计数据请求异常: {e}")
    
    # 2. 测试最近测评数据API
    print("\n2. 测试最近测评数据API...")
    try:
        response = requests.get(f"{base_url}/dashboard/recent-assessments?limit=5")
        if response.status_code == 200:
            assessments = response.json()
            print(f"✓ 最近测评数据获取成功，共 {len(assessments)} 条记录")
            if assessments:
                for i, assessment in enumerate(assessments[:3], 1):
                    print(f"  {i}. {assessment['name']} - {assessment['paper_name']} - {assessment['score']}分")
            else:
                print("  - 暂无测评数据")
        else:
            print(f"✗ 最近测评数据获取失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 最近测评数据请求异常: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_dashboard_complete() 