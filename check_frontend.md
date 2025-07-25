# 前端访问指南

现在前后端API路径已修复，请按照以下步骤测试功能：

1. 确保后端服务器正在运行
```bash
cd backend
uvicorn app.main:app --reload
```

2. 确保前端服务器正在运行
```bash
cd frontend
npm run dev
```

3. 打开浏览器，访问前端页面
- 打开 http://localhost:3000
- 登录系统（使用管理员账号）
- 导航到"报告模板管理"页面

4. 测试报告模板功能
- 尝试创建新模板
- 尝试使用模板设计器
- 尝试预览模板

如果仍然有问题，请检查浏览器开发者工具中的网络请求和控制台错误。

## 故障排除

如果仍然遇到404错误，请尝试以下步骤：

1. 清除浏览器缓存并强制刷新页面（Ctrl+F5）
2. 检查前端网络请求，确认API路径是否正确
3. 检查后端日志，查看请求是否到达后端

如果遇到CORS错误，确保后端的CORS设置正确：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
``` 