# 人才测评平台 - 前端项目

## 项目简介

这是人才测评平台的前端部分，使用 React + TypeScript + Ant Design 开发，包含被试者界面和管理员界面。

## 技术栈

- React 18
- TypeScript
- Vite
- Ant Design 5
- React Router 6
- Axios

## 项目结构

```
src/
├── layouts/           # 布局组件
│   ├── AdminLayout.tsx      # 管理员布局
│   └── ParticipantLayout.tsx # 被试者布局
├── pages/            # 页面组件
│   ├── Login.tsx           # 登录页面
│   ├── admin/              # 管理员页面
│   │   ├── Dashboard.tsx
│   │   ├── QuestionManagement.tsx
│   │   ├── ParticipantManagement.tsx
│   │   └── ReportManagement.tsx
│   └── participant/        # 被试者页面
│       ├── Profile.tsx
│       ├── Assessment.tsx
│       └── Report.tsx
├── App.tsx           # 主应用组件
├── main.tsx          # 应用入口
└── index.css         # 全局样式
```

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

项目将在 http://localhost:3000 启动

### 3. 构建生产版本

```bash
npm run build
```

## 功能模块

### 被试者界面
- **登录页面**: 用户名密码登录
- **个人信息**: 查看和编辑个人信息
- **在线测评**: 答题界面，支持单选、多选、不定项选择
- **我的报告**: 查看和下载个人测评报告

### 管理员界面
- **仪表盘**: 统计数据和最近测评记录
- **题库管理**: 题目的增删改查，支持Word导入
- **被试者管理**: 被试者账号管理
- **报告管理**: 查看、预览、下载所有报告

## 开发说明

### 路由配置
- `/login` - 登录页面
- `/participant/*` - 被试者界面
- `/admin/*` - 管理员界面

### API 配置
项目配置了代理，前端请求 `/api/*` 会被代理到后端 `http://localhost:8000`

### 状态管理
目前使用 React 的 useState 进行状态管理，后续可考虑引入 Redux 或 Zustand

## 注意事项

1. 确保后端服务在 `http://localhost:8000` 运行
2. 登录后需要根据用户角色跳转到对应界面
3. 部分功能（如Word导入、报告生成）需要后端支持

## 后续开发

1. 完善用户权限验证
2. 实现Word文档导入功能
3. 完善选项配置界面
4. 添加数据导出功能
5. 优化UI/UX设计 