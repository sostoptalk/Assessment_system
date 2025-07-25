#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查后端API的可用性
"""
import requests
import sys
import json
from urllib.parse import urljoin

# 默认API地址
API_BASE_URL = "http://localhost:8000"

def check_api(path):
    """检查API是否可访问"""
    url = urljoin(API_BASE_URL, path)
    try:
        print(f"正在检查API: {url}...")
        response = requests.get(url)
        
        if response.status_code == 200:
            print(f"✅ API可用 ({response.status_code})")
            return True, response.text
        else:
            print(f"❌ API不可用 - 状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False, response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API: {str(e)}")
        return False, str(e)

def check_all_apis():
    """检查所有关键API"""
    print("\n=== 开始检查后端API状态 ===\n")
    
    # 检查根路径
    print("\n1. 检查API根路径...")
    root_ok, _ = check_api("/")
    
    # 检查API文档路径
    print("\n2. 检查API文档...")
    docs_ok, _ = check_api("/docs")
    
    # 检查登录路径
    print("\n3. 检查登录接口...")
    login_ok, _ = check_api("/login")
    
    # 检查报告模板API
    print("\n4. 检查报告模板API...")
    templates_ok, templates_response = check_api("/report-templates")
    
    # 检查试卷API
    print("\n5. 检查试卷API...")
    papers_ok, _ = check_api("/papers")
    
    # 检查维度API
    print("\n6. 检查维度API...")
    dimensions_ok, _ = check_api("/dimensions")
    
    # 检查可用路由
    print("\n7. 检查所有可用路由...")
    routes_ok, routes_response = check_api("/openapi.json")
    if routes_ok:
        try:
            data = json.loads(routes_response)
            print("\n可用路由:")
            for path, methods in data.get("paths", {}).items():
                for method, info in methods.items():
                    print(f"  {method.upper()} {path} - {info.get('summary', '无描述')}")
        except json.JSONDecodeError:
            print("无法解析路由信息")
    
    # 总结
    print("\n=== API检查总结 ===")
    all_ok = all([root_ok, docs_ok, login_ok, templates_ok, papers_ok, dimensions_ok])
    if all_ok:
        print("✅ 所有API检查通过!")
    else:
        print("❌ 部分API检查失败，请检查后端服务!")
        if not templates_ok:
            print("  特别注意: 报告模板API不可用，这可能是前端404错误的原因")
    
    return all_ok

if __name__ == "__main__":
    # 可以从命令行参数接受不同的API地址
    if len(sys.argv) > 1:
        API_BASE_URL = sys.argv[1]
    
    success = check_all_apis()
    if not success:
        sys.exit(1) 