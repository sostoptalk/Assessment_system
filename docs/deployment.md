# 部署说明

## 开发环境部署

### 1. 后端部署
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. 前端部署
```bash
cd frontend
npm install
npm run dev
```

## 生产环境部署

### 使用Docker Compose
```bash
docker-compose up -d
```

### 手动部署
1. 配置数据库
2. 启动后端服务
3. 构建前端
4. 配置Nginx
