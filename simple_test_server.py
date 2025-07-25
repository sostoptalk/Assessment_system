#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTTP测试服务器
用于验证端口和网络连接
"""

import http.server
import socketserver
import threading
import time
import json
import cgi

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试服务器</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
        .success { color: green; }
        .info { color: blue; }
    </style>
</head>
<body>
    <h1 class="success">✅ 测试服务器运行正常！</h1>
    <p class="info">如果您能看到这个页面，说明网络连接正常。</p>
    <p>当前时间: {}</p>
    <p>请求路径: {}</p>
    <p>服务器地址: http://localhost:3001</p>
</body>
</html>
            """.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.path)
            
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f"404 - 页面未找到: {self.path}".encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/login':
            # 获取请求的Content-Type
            content_type = self.headers['Content-Type']
            content_length = int(self.headers['Content-Length']) if 'Content-Length' in self.headers else 0
            
            # 处理不同类型的请求
            if content_type and 'multipart/form-data' in content_type:
                # 处理FormData格式
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                username = form['username'].value if 'username' in form else 'unknown'
                password = form['password'].value if 'password' in form else 'unknown'
                print(f"FormData登录: 用户名={username}, 密码={password}")
            else:
                # 处理JSON或其他格式
                post_data = self.rfile.read(content_length).decode('utf-8')
                try:
                    data = json.loads(post_data)
                    username = data.get('username', 'unknown')
                    password = data.get('password', 'unknown')
                    print(f"JSON登录: 用户名={username}, 密码={password}")
                except:
                    print(f"未知格式: {post_data}")
                    username = 'unknown'
                    password = 'unknown'
            
            # 返回成功的登录响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "access_token": f"mock_token_for_{username}_1234567890",
                "token_type": "bearer",
                "user": {
                    "username": username,
                    "real_name": "测试用户",
                    "role": "admin",
                    "email": f"{username}@example.com"
                }
            }
            
            self.wfile.write(json.dumps(response).encode('utf-8'))
            print(f"登录成功: {json.dumps(response)}")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "404 - API端点未找到"}).encode('utf-8'))

def start_test_server(port=3001):
    """启动测试服务器"""
    with socketserver.TCPServer(("", port), TestHandler) as httpd:
        print(f"🚀 测试服务器启动在端口 {port}")
        print(f"🌐 访问地址: http://localhost:{port}")
        print(f"📝 登录API: http://localhost:{port}/login")
        print("按 Ctrl+C 停止服务器")
        httpd.serve_forever()

if __name__ == "__main__":
    try:
        start_test_server()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止") 