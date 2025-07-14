# 人才测评平台

一个基于FastAPI和React的人才测评系统，支持在线答题、自动评分、报告生成等功能。

## 项目结构

```
Assessment_system/
├── backend/          # 后端代码 (FastAPI)
├── frontend/         # 前端代码 (React)
├── docs/            # 项目文档
└── docker/          # Docker配置
```

## 快速开始

### 使用Docker Compose (推荐)
```bash
# 克隆项目
git clone <repository-url>
cd Assessment_system

# 启动服务
docker-compose up -d
```

### 手动启动
```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

## 功能特性

- 🔐 用户认证与权限管理
- 📝 在线测评系统
- 📊 题库管理
- 📈 报告生成
- 👥 被试者管理
- 📋 试卷管理

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- MySQL
- JWT认证

### 前端
- React 18
- TypeScript
- Ant Design
- Vite

## 文档

- [API文档](docs/api.md)
- [部署说明](docs/deployment.md)
- [开发指南](docs/development.md)

## 许可证

MIT License
