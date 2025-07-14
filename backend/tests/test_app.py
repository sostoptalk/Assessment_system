# -*- coding: utf-8 -*-
"""
FastAPI 测试版本 - 不依赖数据库
用于快速测试前端和后端连接
"""
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

# JWT配置
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 模拟用户数据
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "real_name": "管理员",
        "role": "admin",
        "email": "admin@example.com"
    },
    "user1": {
        "username": "user1", 
        "password": "user123",
        "real_name": "测试用户1",
        "role": "participant",
        "email": "user1@example.com"
    }
}

app = FastAPI(title="人才测评平台API - 测试版", description="测试版本，不依赖数据库")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    real_name: str
    role: str
    email: Optional[str] = None

# 工具函数
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# 测试接口
@app.get("/")
def read_root():
    return {"message": "人才测评平台API - 测试版", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# 用户登录接口
@app.post("/login")
def login(request: LoginRequest):
    user = MOCK_USERS.get(request.username)
    if not user or user["password"] != request.password:
        return {"error": "用户名或密码错误"}
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "real_name": user["real_name"],
            "role": user["role"],
            "email": user["email"]
        }
    }

# 获取用户信息接口
@app.get("/me")
def get_user_info(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"error": "缺少认证token"}
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        return {"error": "无效的token"}
    
    username = payload.get("sub")
    user = MOCK_USERS.get(username)
    
    if not user:
        return {"error": "用户不存在"}
    
    return {
        "username": user["username"],
        "real_name": user["real_name"],
        "role": user["role"],
        "email": user["email"]
    }

# 模拟测评数据接口
@app.get("/assessment/questions")
def get_questions():
    return {
        "questions": [
            {
                "id": 1,
                "question": "在商业决策中，您更倾向于哪种方式？",
                "options": ["数据分析驱动", "直觉判断", "团队讨论", "专家咨询"],
                "type": "single_choice"
            },
            {
                "id": 2,
                "question": "面对市场变化，您会如何应对？",
                "options": ["立即调整策略", "观察一段时间", "咨询上级", "保持现状"],
                "type": "single_choice"
            }
        ]
    }

@app.post("/assessment/submit")
def submit_assessment(answers: dict):
    return {
        "message": "测评提交成功",
        "assessment_id": "test_001",
        "score": 85,
        "level": "优秀"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 