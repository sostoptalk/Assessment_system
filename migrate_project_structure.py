#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构迁移脚本
用于将当前混乱的项目结构整理为规范的结构
"""

import os
import shutil
import json
from pathlib import Path

def create_directory_structure():
    """创建新的目录结构"""
    directories = [
        # 后端目录
        "backend/app/models",
        "backend/app/schemas", 
        "backend/app/api",
        "backend/app/core",
        "backend/app/services",
        "backend/app/utils",
        "backend/tests",
        "backend/scripts",
        "backend/reports/generators",
        "backend/reports/templates",
        "backend/reports/assets",
        "backend/data",
        
        # 前端目录
        "frontend/public",
        "frontend/src/components",
        "frontend/src/services",
        "frontend/src/utils",
        "frontend/src/hooks",
        "frontend/tests",
        
        # 文档目录
        "docs",
        
        # Docker目录
        "docker"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def move_backend_files():
    """移动后端相关文件"""
    backend_moves = [
        # 主程序文件
        ("app.py", "backend/app/main.py"),
        
        # 生成器文件
        ("generator.py", "backend/reports/generators/report_generator.py"),
        ("generator2.py", "backend/reports/generators/report_generator_v2.py"),
        ("chart_generator.py", "backend/reports/generators/chart_generator.py"),
        ("batch_generation_from_excel.py", "backend/reports/generators/batch_generator.py"),
        
        # 数据库脚本
        ("db_init.sql", "backend/scripts/init_db.sql"),
        ("create_paper_tables.sql", "backend/scripts/create_paper_tables.sql"),
        ("migrate_database.py", "backend/scripts/migrate_database.py"),
        
        # 数据文件
        ("data.xlsx", "backend/data/sample_data.xlsx"),
        ("60题V2-管理潜质测评问卷.docx", "backend/data/questionnaire_template.docx"),
        
        # 测试文件
        ("test_api.py", "backend/tests/test_api.py"),
        ("test_app.py", "backend/tests/test_app.py"),
        ("test_assessment_api.py", "backend/tests/test_assessment_api.py"),
        ("test_dashboard_api.py", "backend/tests/test_dashboard_api.py"),
        ("test_dashboard_data.py", "backend/tests/test_dashboard_data.py"),
        ("test_delete_paper.py", "backend/tests/test_delete_paper.py"),
        ("test_delete_question.py", "backend/tests/test_delete_question.py"),
        ("test_dimension_api.py", "backend/tests/test_dimension_api.py"),
        ("test_dimension_frontend.py", "backend/tests/test_dimension_frontend.py"),
        ("test_dimension_question_matching.py", "backend/tests/test_dimension_question_matching.py"),
        ("test_dimension_simple.py", "backend/tests/test_dimension_simple.py"),
        ("test_frontend_request.py", "backend/tests/test_frontend_request.py"),
        ("test_paper_api.py", "backend/tests/test_paper_api.py"),
        ("test_paper_questions.py", "backend/tests/test_paper_questions.py"),
        ("test_profile_api.py", "backend/tests/test_profile_api.py"),
        ("test_question_uniqueness.py", "backend/tests/test_question_uniqueness.py"),
        ("test_real_backend.py", "backend/tests/test_real_backend.py"),
        ("debug_api_errors.py", "backend/tests/debug_api_errors.py"),
        ("debug_assessment_api.py", "backend/tests/debug_assessment_api.py"),
        
        # 用户管理脚本
        ("check_admin_user.py", "backend/scripts/check_admin_user.py"),
        ("create_db_users.py", "backend/scripts/create_db_users.py"),
        ("create_test_users.py", "backend/scripts/create_test_users.py"),
    ]
    
    for src, dst in backend_moves:
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"✅ 移动文件: {src} → {dst}")
        else:
            print(f"⚠️  文件不存在: {src}")

def move_frontend_files():
    """移动前端相关文件"""
    # 移动整个src目录
    if os.path.exists("src"):
        shutil.move("src", "frontend/src")
        print("✅ 移动目录: src → frontend/src")
    
    # 移动前端配置文件
    frontend_moves = [
        ("package.json", "frontend/package.json"),
        ("package-lock.json", "frontend/package-lock.json"),
        ("tsconfig.json", "frontend/tsconfig.json"),
        ("tsconfig.node.json", "frontend/tsconfig.node.json"),
        ("vite.config.ts", "frontend/vite.config.ts"),
        ("index.html", "frontend/public/index.html"),
        ("frontend-readme.md", "frontend/README.md"),
    ]
    
    for src, dst in frontend_moves:
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"✅ 移动文件: {src} → {dst}")
        else:
            print(f"⚠️  文件不存在: {src}")

def move_template_files():
    """移动模板文件"""
    if os.path.exists("templates"):
        # 移动模板文件到后端reports目录
        for file in os.listdir("templates"):
            src = os.path.join("templates", file)
            dst = os.path.join("backend/reports/templates", file)
            shutil.move(src, dst)
            print(f"✅ 移动模板: {src} → {dst}")
        
        # 删除空的templates目录
        os.rmdir("templates")
        print("✅ 删除空目录: templates")

def move_test_html_files():
    """移动HTML测试文件"""
    html_test_files = [
        "test_login.html",
        "test_assessment.html", 
        "test_profile.html"
    ]
    
    for file in html_test_files:
        if os.path.exists(file):
            dst = os.path.join("frontend/tests", file)
            shutil.move(file, dst)
            print(f"✅ 移动HTML测试: {file} → {dst}")

def create_config_files():
    """创建配置文件"""
    
    # 创建requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
python-docx==1.1.0
matplotlib==3.8.2
weasyprint==60.2
jinja2==3.1.2
pandas==2.1.4
openpyxl==3.1.2
"""
    
    with open("backend/requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    print("✅ 创建文件: backend/requirements.txt")
    
    # 创建.env.example
    env_content = """# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/test_assessment
SECRET_KEY=your_secret_key_here

# 前端配置
VITE_API_BASE_URL=http://localhost:8000

# 文件存储
UPLOAD_DIR=./uploads
REPORT_DIR=./reports

# JWT配置
ACCESS_TOKEN_EXPIRE_MINUTES=1440
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✅ 创建文件: .env.example")
    
    # 创建docker-compose.yml
    docker_compose_content = """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://root:password@db:3306/test_assessment
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
      - ./reports:/app/reports

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=test_assessment
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
"""
    
    with open("docker-compose.yml", "w", encoding="utf-8") as f:
        f.write(docker_compose_content)
    print("✅ 创建文件: docker-compose.yml")

def create_docker_files():
    """创建Docker相关文件"""
    
    # 后端Dockerfile
    backend_dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("docker/Dockerfile.backend", "w", encoding="utf-8") as f:
        f.write(backend_dockerfile)
    print("✅ 创建文件: docker/Dockerfile.backend")
    
    # 前端Dockerfile
    frontend_dockerfile = """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""
    
    with open("docker/Dockerfile.frontend", "w", encoding="utf-8") as f:
        f.write(frontend_dockerfile)
    print("✅ 创建文件: docker/Dockerfile.frontend")

def create_documentation():
    """创建文档文件"""
    
    # API文档
    api_doc = """# API 文档

## 认证接口

### POST /login
用户登录接口

### POST /register  
用户注册接口

### GET /me
获取当前用户信息

## 题库管理

### GET /questions
获取题目列表

### POST /questions
创建新题目

### PUT /questions/{question_id}
更新题目

### DELETE /questions/{question_id}
删除题目

## 试卷管理

### GET /papers
获取试卷列表

### POST /papers
创建新试卷

### PUT /papers/{paper_id}
更新试卷

### DELETE /papers/{paper_id}
删除试卷

## 用户管理

### GET /participants
获取被试者列表

### POST /participants
创建被试者

### PUT /participants/{participant_id}
更新被试者信息

### DELETE /participants/{participant_id}
删除被试者
"""
    
    with open("docs/api.md", "w", encoding="utf-8") as f:
        f.write(api_doc)
    print("✅ 创建文件: docs/api.md")
    
    # 部署文档
    deployment_doc = """# 部署说明

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
"""
    
    with open("docs/deployment.md", "w", encoding="utf-8") as f:
        f.write(deployment_doc)
    print("✅ 创建文件: docs/deployment.md")

def update_readme():
    """更新主README文件"""
    new_readme_content = """# 人才测评平台

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
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme_content)
    print("✅ 更新文件: README.md")

def main():
    """主函数"""
    print("🚀 开始项目结构迁移...")
    
    # 1. 创建目录结构
    print("\n📁 创建目录结构...")
    create_directory_structure()
    
    # 2. 移动后端文件
    print("\n📦 移动后端文件...")
    move_backend_files()
    
    # 3. 移动前端文件
    print("\n🎨 移动前端文件...")
    move_frontend_files()
    
    # 4. 移动模板文件
    print("\n📄 移动模板文件...")
    move_template_files()
    
    # 5. 移动HTML测试文件
    print("\n🧪 移动HTML测试文件...")
    move_test_html_files()
    
    # 6. 创建配置文件
    print("\n⚙️  创建配置文件...")
    create_config_files()
    
    # 7. 创建Docker文件
    print("\n🐳 创建Docker文件...")
    create_docker_files()
    
    # 8. 创建文档
    print("\n📚 创建文档...")
    create_documentation()
    
    # 9. 更新README
    print("\n📝 更新README...")
    update_readme()
    
    print("\n✅ 项目结构迁移完成！")
    print("\n📋 后续步骤:")
    print("1. 检查迁移后的文件结构")
    print("2. 更新import路径")
    print("3. 测试功能是否正常")
    print("4. 提交代码到版本控制")

if __name__ == "__main__":
    main() 