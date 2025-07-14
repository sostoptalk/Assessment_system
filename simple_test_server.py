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

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
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
    <p>服务器地址: http://localhost:3003</p>
</body>
</html>
            """.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.path)
            
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"404 - 页面未找到: {self.path}".encode('utf-8'))

def start_test_server(port=3003):
    """启动测试服务器"""
    with socketserver.TCPServer(("", port), TestHandler) as httpd:
        print(f"🚀 测试服务器启动在端口 {port}")
        print(f"🌐 访问地址: http://localhost:{port}")
        print("按 Ctrl+C 停止服务器")
        httpd.serve_forever()

if __name__ == "__main__":
    try:
        start_test_server()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止") 