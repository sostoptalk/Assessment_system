# -*- coding: utf-8 -*-
"""
FastAPI 后端主程序
- 启动命令: uvicorn app:app --reload
- 包含数据库连接、用户模型、基础注册/登录接口
- 中文注释
"""
from sqlalchemy import text
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, File, UploadFile, Body, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, selectinload, relationship
from passlib.context import CryptContext
from datetime import datetime, timedelta
import enum
import jwt
from sqlalchemy.types import JSON as SQLAlchemyJSON
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
import docx
import io
import json
from collections import defaultdict
from fastapi.routing import APIRoute
import pandas as pd
import re
# 导入Report模型，但需要确保在Base定义之后导入

print("=== 3当前 main.py 被加载 ===")

# 数据库配置
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Yrui2997@localhost:3306/test_assessment?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT密钥
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# 用户角色枚举
class UserRole(str, enum.Enum):
    admin = "admin"
    participant = "participant"

# 用户表模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    role = Column(Enum(UserRole), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gender = Column(String(10))  # 性别
    age = Column(Integer)       # 年龄
    position = Column(String(100))  # 岗位
    
    # 关联关系
    reports = relationship("Report", back_populates="user")

# 题库表模型
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)
    options = Column(SQLAlchemyJSON, nullable=False)
    scores = Column(SQLAlchemyJSON, nullable=False)
    shuffle_options = Column(Boolean, default=False)  # 是否启用选项乱序
    dimension_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)  # 所属维度
    parent_case_id = Column(Integer, nullable=True)  # 新增
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 试卷表模型
class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    duration = Column(Integer, nullable=False)  # 答题时间（分钟）
    status = Column(String(20), default="draft")  # draft, published, closed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    reports = relationship("Report", back_populates="paper")

# 维度表
class Dimension(Base):
    __tablename__ = "dimensions"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)  # 父维度ID，用于小维度
    name = Column(String(100), nullable=False)  # 维度名称
    description = Column(Text, nullable=True)  # 维度描述
    weight = Column(Float, default=1.0)  # 权重
    order_num = Column(Integer, default=0)  # 排序
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    paper = relationship("Paper", backref="dimensions")
    parent = relationship("Dimension", remote_side=[id], backref="children")
    questions = relationship("Question", backref="dimension")

# 试卷题目关联表
class PaperQuestion(Base):
    __tablename__ = "paper_questions"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)  # 所属维度
    order_num = Column(Integer, nullable=False)  # 题目顺序
    is_shuffled = Column(Boolean, default=False)  # 是否启用题目乱序
    shuffle_seed = Column(Integer)  # 乱序种子
    shuffled_order = Column(SQLAlchemyJSON)  # 乱序后的题目顺序
    created_at = Column(DateTime, default=datetime.utcnow)

# 试卷分配表
class PaperAssignment(Base):
    __tablename__ = "paper_assignments"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="assigned")  # assigned, started, completed
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    question_order = Column(SQLAlchemyJSON)  # 该用户本次测试的题目顺序
    option_orders = Column(SQLAlchemyJSON)  # 该用户本次测试的选项顺序
    # 新增：与Paper的关系
    paper = relationship("Paper", backref="assignments")
    # 新增：与User的关系
    user = relationship("User", backref="paper_assignments")

# Pydantic模型
class QuestionCreate(BaseModel):
    content: str
    type: str
    options: List[str]
    scores: List[int]
    shuffle_options: bool = False
    parent_case_id: Optional[int] = None  # 新增

class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    type: Optional[str] = None
    options: Optional[List[str]] = None
    scores: Optional[List[int]] = None
    shuffle_options: Optional[bool] = None
    parent_case_id: Optional[int] = None  # 新增

class QuestionOut(BaseModel):
    id: int
    content: str
    type: str
    options: list
    scores: list
    shuffle_options: bool
    parent_case_id: Optional[int] = None  # 新增
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class PaperCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int

class PaperUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[str] = None

class PaperOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    duration: int
    status: str
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class PaperAssignmentCreate(BaseModel):
    user_ids: List[int]

class QuestionIdsRequest(BaseModel):
    question_ids: List[int]

class QuestionWithDimensionRequest(BaseModel):
    question_id: int
    dimension_id: Optional[int] = None

# 维度相关模型
class DimensionCreate(BaseModel):
    paper_id: int
    parent_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    weight: float = 1.0
    order_num: int = 0

class DimensionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = None
    order_num: Optional[int] = None

class DimensionOut(BaseModel):
    id: int
    paper_id: int
    parent_id: Optional[int]
    name: str
    description: Optional[str]
    weight: float
    order_num: int
    created_at: datetime
    updated_at: datetime
    children: List['DimensionOut'] = []
    
    class Config:
        orm_mode = True
        # 解决循环引用问题
        from_attributes = True

class ParticipantCreate(BaseModel):
    username: str
    password: str
    real_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True

class ParticipantUpdate(BaseModel):
    username: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class ParticipantOut(BaseModel):
    id: int
    username: str
    real_name: str
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Report模型定义
class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    file_path = Column(String(500), nullable=False)  # 报告文件路径
    file_name = Column(String(200), nullable=False)  # 报告文件名
    file_size = Column(Integer)  # 文件大小（字节）
    status = Column(String(20), default="completed")  # completed, failed
    error_message = Column(Text)  # 错误信息
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="reports")
    paper = relationship("Paper", back_populates="reports")

# 创建所有表
Base.metadata.create_all(bind=engine)

# FastAPI 实例
app = FastAPI(title="人才测评平台API", description="后端服务，含用户注册/登录等基础功能")

# 注册路由信息打印
@app.on_event("startup")
def print_routes():
    print("\n=== FastAPI 路由注册信息 ===")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"{route.path}  |  {route.methods}  |  {route.name}")
    print("=== 路由打印结束 ===\n")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3008"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 工具函数：密码加密与校验
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 工具函数：生成JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 用户注册接口（仅管理员可用，实际应加权限校验）
@app.post("/register", summary="注册用户（管理员分配账号）")
def register_user(username: str, password: str, real_name: str = "", role: UserRole = UserRole.participant, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=username,
        password_hash=get_password_hash(password),
        real_name=real_name,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "注册成功", "user_id": user.id}

# 用户登录接口
@app.post("/login", summary="用户登录，返回JWT Token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, str(user.password_hash)):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not bool(user.is_active):
        raise HTTPException(status_code=403, detail="账号未激活")
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# 示例受保护接口
@app.get("/me", summary="获取当前用户信息（需登录）")
@app.get("/me/", summary="获取当前用户信息（需登录）")
def read_users_me(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "age": user.age,
        "position": user.position
    }

# 用户信息更新模型
class UserProfileUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    position: Optional[str] = None

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

# 更新用户基本信息（邮箱、手机号）
@app.put("/me/profile", summary="更新用户基本信息")
@app.put("/me/profile/", summary="更新用户基本信息")
def update_user_profile(
    profile_update: UserProfileUpdate,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新邮箱、手机号、性别、年龄、岗位
    if profile_update.email is not None:
        user.email = profile_update.email
    if profile_update.phone is not None:
        user.phone = profile_update.phone
    if profile_update.gender is not None:
        user.gender = profile_update.gender
    if profile_update.age is not None:
        user.age = profile_update.age
    if profile_update.position is not None:
        user.position = profile_update.position
    
    db.commit()
    db.refresh(user)
    
    return {
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "email": user.email,
        "phone": user.phone,
        "gender": user.gender,
        "age": user.age,
        "position": user.position
    }

# 更新用户密码
@app.put("/me/password", summary="更新用户密码")
@app.put("/me/password/", summary="更新用户密码")
def update_user_password(
    password_update: UserPasswordUpdate,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证旧密码
    if not verify_password(password_update.old_password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail="原密码错误")
    
    # 更新密码
    user.password_hash = get_password_hash(password_update.new_password)
    
    db.commit()
    
    return {"msg": "密码更新成功"}

# 被试者测试相关API
@app.get("/my-assignments", summary="获取当前用户的试卷分配")
@app.get("/my-assignments/", summary="获取当前用户的试卷分配")
def get_my_assignments(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户的试卷分配，并自动加载关联的paper对象
    assignments = db.query(PaperAssignment).options(
        selectinload(PaperAssignment.paper)
    ).filter(
        PaperAssignment.user_id == user.id
    ).order_by(PaperAssignment.assigned_at.desc()).all()
    
    result = []
    for assignment in assignments:
        # 兼容paper为None的情况
        paper = assignment.paper
        result.append({
            "id": assignment.id,
            "paper_id": assignment.paper_id,
            "paper_name": paper.name if paper else None,
            "paper_description": paper.description if paper else None,
            "duration": paper.duration if paper else None,
            "status": assignment.status,
            "assigned_at": assignment.assigned_at.strftime("%Y-%m-%d %H:%M:%S") if assignment.assigned_at else None,
            "started_at": assignment.started_at.strftime("%Y-%m-%d %H:%M:%S") if assignment.started_at else None,
            "completed_at": assignment.completed_at.strftime("%Y-%m-%d %H:%M:%S") if assignment.completed_at else None
        })
    
    return result

# 开始测试
from datetime import datetime

@app.post("/start-assessment/{assignment_id}", summary="开始测试")
def start_assessment(
    assignment_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id,
        PaperAssignment.user_id == user.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="试卷分配不存在")
    if assignment.status == "assigned":
        assignment.status = "started"
        assignment.started_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
    # 获取试卷题目
    paper = db.query(Paper).filter(Paper.id == assignment.paper_id).first()
    paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper.id).order_by(PaperQuestion.order_num).all()
    questions = []
    for pq in paper_questions:
        question = db.query(Question).filter(Question.id == pq.question_id).first()
        if question:
            questions.append({
                "id": question.id,
                "content": question.content,
                "type": question.type,
                "options": question.options,
                "scores": question.scores,
                "order_num": pq.order_num,
                "parent_case_id": getattr(question, 'parent_case_id', None)  # 新增
            })
    return {
        "assignment_id": assignment.id,
        "paper_id": paper.id,
        "paper_name": paper.name,
        "duration": paper.duration,
        "questions": questions,
        "status": assignment.status,
        "started_at": assignment.started_at.strftime("%Y-%m-%d %H:%M:%S") if assignment.started_at else None
    }

class SubmitAssessmentRequest(BaseModel):
    answers: dict

@app.post("/submit-assessment/{assignment_id}", summary="提交测试答案")
@app.post("/submit-assessment/{assignment_id}/", summary="提交测试答案")
def submit_assessment(
    assignment_id: int,
    request: SubmitAssessmentRequest,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查试卷分配是否存在且属于当前用户
    assignment = db.query(PaperAssignment).filter(
        PaperAssignment.id == assignment_id,
        PaperAssignment.user_id == user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="试卷分配不存在")
    
    if assignment.status != "started":
        raise HTTPException(status_code=400, detail="试卷未开始或已完成")
    
    # 保存每道题的答案到 answers 表
    paper_id = assignment.paper_id
    now = datetime.utcnow()
    
    # 获取题目信息用于计算分数
    question_ids = [int(qid) for qid in request.answers.keys()]
    questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
    question_score_map = {q.id: q.scores for q in questions}
    
    for qid, ans in request.answers.items():
        question_id = int(qid)
        
        # 计算分数
        score = None
        if question_id in question_score_map:
            q_scores = question_score_map[question_id]
            
            # 解析答案获取选项索引
            idx = None
            if isinstance(ans, list) and len(ans) > 0:
                if isinstance(ans[0], int):
                    idx = ans[0]
                elif isinstance(ans[0], str):
                    idx = ord(ans[0].upper()) - ord('A')
            elif isinstance(ans, str):
                idx = ord(ans.upper()) - ord('A')
            
            # 计算分数
            if idx is not None and 0 <= idx < len(q_scores):
                score = q_scores[idx]
            else:
                score = 0  # 无效答案给0分
        
        try:
            print(f"正在插入答案: user_id={user.id}, question_id={question_id}, answer={ans}, score={score}")
            # 使用SQLAlchemy的text()函数来执行原生SQL
            from sqlalchemy import text
            db.execute(
                text("INSERT INTO answers (user_id, question_id, answer, score, answered_at) VALUES (:user_id, :question_id, :answer, :score, :answered_at)"),
                {
                    "user_id": user.id,
                    "question_id": question_id,
                    "answer": json.dumps(ans, ensure_ascii=False),
                    "score": score,
                    "answered_at": now
                }
            )
            print(f"✅ 成功插入答案记录，分数: {score}")
        except Exception as e:
            print(f"❌ 插入答案记录失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            # 继续执行，不中断整个提交过程
    
    # 更新状态为已完成
    assignment.status = "completed"
    assignment.completed_at = now
    db.commit()
    
    return {"msg": "测试提交成功", "completed_at": assignment.completed_at.strftime("%Y-%m-%d %H:%M:%S")}

router = APIRouter(prefix="/questions", tags=["题库管理"])

# 获取题目列表
@router.get("/", response_model=List[QuestionOut])
@router.get("", response_model=List[QuestionOut])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(Question).order_by(Question.id.desc()).all()
    return questions

# 新增题目
@router.post("/", response_model=QuestionOut)
@router.post("", response_model=QuestionOut)
def create_question(q: QuestionCreate, db: Session = Depends(get_db)):
    question = Question(
        content=q.content,
        type=q.type,
        options=q.options,
        scores=q.scores,
        shuffle_options=q.shuffle_options if hasattr(q, 'shuffle_options') else False,
        parent_case_id=q.parent_case_id
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

# 修改题目
@router.put("/{question_id}", response_model=QuestionOut)
def update_question(question_id: int, q: QuestionUpdate, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    for field, value in q.dict(exclude_unset=True).items():
        setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question

# 删除题目
@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """删除题目（先检查是否被分配到试卷/有答题记录）"""
    try:
        # 检查题目是否存在
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在")
        # 检查是否有答题记录
        answer_count = db.execute(
            text("SELECT COUNT(*) FROM answers WHERE question_id = :qid"),
            {"qid": question_id}
        ).scalar()
        if answer_count > 0:
            raise HTTPException(status_code=400, detail="该题目已有答题记录，无法删除。")
        # 检查是否被分配到试卷
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.question_id == question_id).all()
        if paper_questions:
            # 查询所有分配的试卷
            paper_ids = list(set([pq.paper_id for pq in paper_questions]))
            papers = db.query(Paper).filter(Paper.id.in_(paper_ids)).all()
            paper_names = [f"{p.name}(ID:{p.id})" for p in papers]
            raise HTTPException(status_code=400, detail=f"题目已被分配给试卷：{', '.join(paper_names)}，请先在试卷管理界面移除该题目后再删除。")
        # 删除题目
        db.delete(question)
        db.commit()
        return {"msg": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除题目失败: {str(e)}")

# Word导入题库（预留接口）
@router.post("/import_word")
def import_questions_from_word(file: UploadFile = File(...)):
    # 读取上传的Word文件
    content = file.file.read()
    doc = docx.Document(io.BytesIO(content))
    questions = []
    current_question = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # 题目编号（如"题目1"）
        if text.startswith("题目"):
            if current_question:
                questions.append(current_question)
            current_question = {
                "content": "",
                "type": "single",
                "options": [],
                "scores": []
            }
        elif text.startswith("场景：") or text.startswith("场景:"):
            if current_question is not None:
                current_question["content"] = text
        elif text[0] in "ABCD" and (text[1] == '.' or text[1] == '．'):
            # 选项，如"A.内容"
            if current_question is not None:
                # 用正则去除A./B./C./D.等前缀
                clean_text = re.sub(r'^[A-DＡ-Ｄa-dａ-ｄ][\.、．\)]\s*', '', text)
                current_question["options"].append(clean_text)
        else:
            # 兼容没有"场景："的题干
            if current_question is not None and not current_question["content"]:
                current_question["content"] = text
    if current_question:
        questions.append(current_question)
    # 设置默认分数 [10,7,4,1]，多于4个后续为0
    for q in questions:
        n = len(q["options"])
        default_scores = [10, 7, 4, 1] + [0] * (n - 4) if n > 4 else [10, 7, 4, 1][:n]
        q["scores"] = default_scores
    return {"questions": questions}

# 试卷管理路由
paper_router = APIRouter(prefix="/papers", tags=["试卷管理"])

# 获取试卷列表
@paper_router.get("/", response_model=List[PaperOut])
@paper_router.get("", response_model=List[PaperOut])
def get_papers(db: Session = Depends(get_db)):
    papers = db.query(Paper).order_by(Paper.id.desc()).all()
    return papers

# 创建试卷
@paper_router.post("/", response_model=PaperOut)
@paper_router.post("", response_model=PaperOut)
def create_paper(p: PaperCreate, db: Session = Depends(get_db)):
    paper = Paper(
        name=p.name,
        description=p.description,
        duration=p.duration
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper

# 更新试卷
@paper_router.put("/{paper_id}", response_model=PaperOut)
def update_paper(paper_id: str, p: PaperUpdate, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    for field, value in p.dict(exclude_unset=True).items():
        setattr(paper, field, value)
    db.commit()
    db.refresh(paper)
    return paper

# 删除试卷
@paper_router.delete("/{paper_id}")
def delete_paper(paper_id: str, db: Session = Depends(get_db)):
    """删除试卷（自动删除所有相关重做申请和分配记录）"""
    try:
        paper_id_int = int(paper_id)
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        # 检查是否还有题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id_int).all()
        if paper_questions:
            # 查询所有题目
            question_ids = [pq.question_id for pq in paper_questions]
            questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
            question_infos = [f"{q.content[:20]}...(ID:{q.id})" for q in questions]
            raise HTTPException(status_code=400, detail=f"试卷下还有题目未移除：{', '.join(question_infos)}，请先删除所有分配给该试卷的题目后再删除试卷。")
        # 1. 先删除试卷分配记录前，先删除所有相关redo_requests
        assignments = db.query(PaperAssignment).filter(PaperAssignment.paper_id == paper_id_int).all()
        assignment_ids = [a.id for a in assignments]
        if assignment_ids:
            db.execute(text("DELETE FROM redo_requests WHERE assignment_id IN :ids"), {"ids": tuple(assignment_ids)})
        for assignment in assignments:
            db.delete(assignment)
        # 2. 删除试卷维度（先删除子维度，再删除父维度）
        child_dimensions = db.query(Dimension).filter(
            Dimension.paper_id == paper_id_int,
            Dimension.parent_id.isnot(None)
        ).all()
        for child_dim in child_dimensions:
            db.delete(child_dim)
        parent_dimensions = db.query(Dimension).filter(
            Dimension.paper_id == paper_id_int,
            Dimension.parent_id.is_(None)
        ).all()
        for parent_dim in parent_dimensions:
            db.delete(parent_dim)
        # 3. 最后删除试卷本身
        db.delete(paper)
        db.commit()
        return {"msg": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除试卷失败: {str(e)}")

# 获取试卷分配情况
@paper_router.get("/{paper_id}/list-assignment")
@paper_router.get("/{paper_id}/list-assignment/")
def get_paper_assignments(paper_id: str, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    assignments = db.query(PaperAssignment).filter(
        PaperAssignment.paper_id == paper_id_int
    ).all()
    result = []
    for assignment in assignments:
        user = db.query(User).filter(User.id == assignment.user_id).first()
        if user:
            result.append({
                "id": assignment.id,
                "user_id": assignment.user_id,
                "user_name": user.real_name or user.username,
                "username": user.username,
                "status": assignment.status,
                "assigned_at": assignment.assigned_at,
                "started_at": assignment.started_at,
                "completed_at": assignment.completed_at
            })
    return result

# 获取试卷题目
@paper_router.get("/{paper_id}/questions")
@paper_router.get("/{paper_id}/questions/")
def get_paper_questions(paper_id: str, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper_questions = db.query(PaperQuestion).filter(
        PaperQuestion.paper_id == paper_id_int
    ).order_by(PaperQuestion.order_num).all()
    questions = []
    for pq in paper_questions:
        question = db.query(Question).filter(Question.id == pq.question_id).first()
        if question:
            # 获取维度信息
            dimension_info = None
            if pq.dimension_id:
                dimension = db.query(Dimension).filter(Dimension.id == pq.dimension_id).first()
                if dimension:
                    dimension_info = {
                        "id": dimension.id,
                        "name": dimension.name,
                        "description": dimension.description,
                        "weight": dimension.weight
                    }
            # 将选项和分数合并成前端期望的格式
            formatted_options = []
            options = question.options if question.options else []
            scores = question.scores if question.scores else []
            labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            for i, (option, score) in enumerate(zip(options, scores)):
                if i < len(labels):
                    formatted_options.append({
                        "label": labels[i],
                        "text": option,
                        "score": score
                    })
            questions.append({
                "id": question.id,
                "content": question.content,
                "type": question.type,
                "options": formatted_options,
                "order_num": pq.order_num,
                "dimension": dimension_info,
                "parent_case_id": question.parent_case_id
            })
    return {"questions": questions}

# 发布试卷
@paper_router.post("/{paper_id}/publish")
@paper_router.post("/{paper_id}/publish/")
def publish_paper(paper_id: str, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    paper.status = "published"
    participants = db.query(User).filter(User.role == UserRole.participant).all()
    for participant in participants:
        existing = db.query(PaperAssignment).filter(
            PaperAssignment.paper_id == paper_id_int,
            PaperAssignment.user_id == participant.id
        ).first()
        if not existing:
            assignment_record = PaperAssignment(
                paper_id=paper_id_int,
                user_id=participant.id
            )
            db.add(assignment_record)
    db.commit()
    return {"msg": "试卷发布成功，已分配给所有被试者"}

# 分配试卷
@paper_router.post("/{paper_id}/assign")
@paper_router.post("/{paper_id}/assign/")
def assign_paper(paper_id: str, assignment: PaperAssignmentCreate, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    for user_id in assignment.user_ids:
        existing = db.query(PaperAssignment).filter(
            PaperAssignment.paper_id == paper_id_int,
            PaperAssignment.user_id == user_id
        ).first()
        if existing:
            if existing.status == "completed":
                existing.status = "assigned"
                existing.completed_at = None
                existing.started_at = None
        else:
            assignment_record = PaperAssignment(
                paper_id=paper_id_int,
                user_id=user_id
            )
            db.add(assignment_record)
    db.commit()
    return {"msg": "分配成功"}

# 添加题目到试卷
@paper_router.post("/{paper_id}/questions")
@paper_router.post("/{paper_id}/questions/")
def add_questions_to_paper(paper_id: str, questions: List[QuestionWithDimensionRequest], db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    max_order = db.query(PaperQuestion).filter(
        PaperQuestion.paper_id == paper_id_int
    ).order_by(PaperQuestion.order_num.desc()).first()
    current_order = (max_order.order_num if max_order else 0) + 1
    for question_req in questions:
        question = db.query(Question).filter(Question.id == question_req.question_id).first()
        if not question:
            continue
        if question_req.dimension_id:
            dimension = db.query(Dimension).filter(
                Dimension.id == question_req.dimension_id,
                Dimension.paper_id == paper_id_int
            ).first()
            if not dimension:
                continue
        existing = db.query(PaperQuestion).filter(
            PaperQuestion.paper_id == paper_id_int,
            PaperQuestion.question_id == question_req.question_id
        ).first()
        if not existing:
            paper_question = PaperQuestion(
                paper_id=paper_id_int,
                question_id=question_req.question_id,
                dimension_id=question_req.dimension_id,
                order_num=current_order
            )
            db.add(paper_question)
            current_order += 1
    db.commit()
    return {"msg": "添加成功"}

@paper_router.delete("/{paper_id}/assignment/{assignment_id}")
def revoke_assignment(paper_id: int, assignment_id: int, db: Session = Depends(get_db)):
    """撤销单个试卷分配（同时删除相关重做申请）"""
    try:
        assignment = db.query(PaperAssignment).filter(PaperAssignment.id == assignment_id, PaperAssignment.paper_id == paper_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="分配记录不存在")
        # 删除相关重做申请
        db.execute(text("DELETE FROM redo_requests WHERE assignment_id = :aid"), {"aid": assignment_id})
        db.delete(assignment)
        db.commit()
        return {"msg": "撤销分配成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"撤销分配失败: {str(e)}")

@paper_router.delete("/{paper_id}/assignments")
def revoke_all_assignments(paper_id: int, db: Session = Depends(get_db)):
    """撤销该试卷的所有分配（同时删除相关重做申请）"""
    try:
        assignments = db.query(PaperAssignment).filter(PaperAssignment.paper_id == paper_id).all()
        assignment_ids = [a.id for a in assignments]
        if assignment_ids:
            db.execute(text("DELETE FROM redo_requests WHERE assignment_id IN :ids"), {"ids": tuple(assignment_ids)})
        for assignment in assignments:
            db.delete(assignment)
        db.commit()
        return {"msg": "已撤销全部分配"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"撤销全部分配失败: {str(e)}")


# 删除试卷题目
@paper_router.delete("/{paper_id}/questions")
@paper_router.delete("/{paper_id}/questions/")
def delete_questions_from_paper(paper_id: str, request: QuestionIdsRequest, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    deleted_count = 0
    for question_id in request.question_ids:
        paper_question = db.query(PaperQuestion).filter(
            PaperQuestion.paper_id == paper_id_int,
            PaperQuestion.question_id == question_id
        ).first()
        if paper_question:
            db.delete(paper_question)
            deleted_count += 1
    db.commit()
    return {"msg": f"成功删除 {deleted_count} 道题目"}

# 题目乱序相关API
@app.post("/papers/{paper_id}/shuffle-questions", summary="启用/禁用题目乱序")
def toggle_question_shuffle(
    paper_id: int,
    enable_shuffle: bool = Body(..., embed=True),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """启用或禁用试卷的题目乱序功能"""
    try:
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 获取试卷的所有题目
        questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        if not questions:
            raise HTTPException(status_code=400, detail="试卷没有题目")
        
        if enable_shuffle:
            # 启用乱序
            import random
            import json
            
            # 生成随机种子
            shuffle_seed = random.randint(1, 999999)
            
            # 获取题目ID列表
            question_ids = [q.question_id for q in questions]
            
            # 使用种子生成随机顺序
            random.seed(shuffle_seed)
            shuffled_ids = question_ids.copy()
            random.shuffle(shuffled_ids)
            
            # 更新所有题目的乱序设置
            for question in questions:
                question.is_shuffled = True
                question.shuffle_seed = shuffle_seed
                question.shuffled_order = shuffled_ids
            
            db.commit()
            
            return {
                "message": "题目乱序已启用",
                "shuffle_seed": shuffle_seed,
                "question_count": len(questions),
                "shuffled_order": shuffled_ids
            }
        else:
            # 禁用乱序
            for question in questions:
                question.is_shuffled = False
                question.shuffle_seed = None
                question.shuffled_order = None
            
            db.commit()
            
            return {"message": "题目乱序已禁用"}
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"设置题目乱序失败: {str(e)}")

@app.get("/papers/{paper_id}/shuffle-status", summary="获取题目乱序状态")
def get_shuffle_status(
    paper_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """获取试卷的题目乱序状态"""
    try:
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 获取第一个题目的乱序状态（所有题目应该一致）
        first_question = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).first()
        
        if not first_question:
            return {
                "paper_id": paper_id,
                "is_shuffled": False,
                "shuffle_seed": None,
                "question_count": 0
            }
        
        return {
            "paper_id": paper_id,
            "is_shuffled": first_question.is_shuffled,
            "shuffle_seed": first_question.shuffle_seed,
            "question_count": db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).count(),
            "shuffled_order": first_question.shuffled_order if first_question.is_shuffled else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取乱序状态失败: {str(e)}")

@app.get("/papers/{paper_id}/questions", summary="获取试卷题目（支持乱序）")
def get_paper_questions_with_shuffle(
    paper_id: int,
    user_id: int = Query(None, description="用户ID，用于获取个人题目顺序"),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """获取试卷题目，支持乱序功能"""
    try:
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 获取试卷题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        
        if not paper_questions:
            return {"questions": []}
        
        # 检查是否启用乱序
        is_shuffled = paper_questions[0].is_shuffled if paper_questions else False
        
        if is_shuffled and user_id:
            # 如果启用乱序且有用户ID，检查用户是否有个人题目顺序
            assignment = db.query(PaperAssignment).filter(
                PaperAssignment.paper_id == paper_id,
                PaperAssignment.user_id == user_id
            ).first()
            
            if assignment and assignment.question_order:
                # 使用用户的个人题目顺序
                question_order = assignment.question_order
            else:
                # 使用试卷的乱序顺序
                question_order = paper_questions[0].shuffled_order
                
            # 按乱序顺序重新排列题目
            question_map = {pq.question_id: pq for pq in paper_questions}
            ordered_questions = []
            
            for q_id in question_order:
                if q_id in question_map:
                    ordered_questions.append(question_map[q_id])
        else:
            # 使用原始顺序
            ordered_questions = sorted(paper_questions, key=lambda x: x.order_num)
        
        # 获取题目详细信息
        question_ids = [pq.question_id for pq in ordered_questions]
        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        question_map = {q.id: q for q in questions}
        
        # 组装返回数据
        result = []
        for i, pq in enumerate(ordered_questions):
            question = question_map.get(pq.question_id)
            if question:
                result.append({
                    "id": question.id,
                    "content": question.content,
                    "type": question.type,
                    "options": question.options,
                    "scores": question.scores,
                    "dimension_id": pq.dimension_id,
                    "order_num": i + 1,  # 显示顺序
                    "original_order": pq.order_num,  # 原始顺序
                    "parent_case_id": question.parent_case_id
                })
        
        return {
            "paper_id": paper_id,
            "is_shuffled": is_shuffled,
            "questions": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取试卷题目失败: {str(e)}")

@app.get("/papers/{paper_id}/questions-with-options", summary="获取试卷题目（支持选项乱序）")
def get_paper_questions_with_option_shuffle(
    paper_id: int,
    user_id: int = Query(None, description="用户ID，用于获取个人选项顺序"),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """获取试卷题目，支持选项乱序功能"""
    try:
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 获取试卷题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        
        if not paper_questions:
            return {"questions": []}
        
        # 检查是否启用题目乱序
        is_shuffled = paper_questions[0].is_shuffled if paper_questions else False
        
        if is_shuffled and user_id:
            # 如果启用题目乱序且有用户ID，检查用户是否有个人题目顺序
            assignment = db.query(PaperAssignment).filter(
                PaperAssignment.paper_id == paper_id,
                PaperAssignment.user_id == user_id
            ).first()
            
            if assignment and assignment.question_order:
                # 使用用户的个人题目顺序
                question_order = assignment.question_order
            else:
                # 使用试卷的乱序顺序
                question_order = paper_questions[0].shuffled_order
                
            # 按乱序顺序重新排列题目
            question_map = {pq.question_id: pq for pq in paper_questions}
            ordered_questions = []
            
            for q_id in question_order:
                if q_id in question_map:
                    ordered_questions.append(question_map[q_id])
        else:
            # 使用原始顺序
            ordered_questions = sorted(paper_questions, key=lambda x: x.order_num)
        
        # 获取题目详细信息
        question_ids = [pq.question_id for pq in ordered_questions]
        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        question_map = {q.id: q for q in questions}
        
        # 获取用户的选项顺序
        option_orders = {}
        if user_id:
            assignment = db.query(PaperAssignment).filter(
                PaperAssignment.paper_id == paper_id,
                PaperAssignment.user_id == user_id
            ).first()
            
            if assignment and assignment.option_orders:
                option_orders = assignment.option_orders
        
        # 组装返回数据
        result = []
        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, pq in enumerate(ordered_questions):
            question = question_map.get(pq.question_id)
            if question:
                # 处理选项顺序
                original_options = question.options
                original_scores = question.scores
                if question.shuffle_options and question.id in option_orders:
                    option_order = option_orders[question.id]
                    shuffled_options = [original_options[j] for j in option_order]
                    shuffled_scores = [original_scores[j] for j in option_order]
                else:
                    shuffled_options = original_options
                    shuffled_scores = original_scores
                # 组装前端需要的格式
                formatted_options = []
                for idx, (opt, score) in enumerate(zip(shuffled_options, shuffled_scores)):
                    formatted_options.append({
                        "label": labels[idx] if idx < len(labels) else chr(65 + idx),
                        "text": opt,
                        "score": score
                    })
                result.append({
                    "id": question.id,
                    "content": question.content,
                    "type": question.type,
                    "options": formatted_options,
                    "shuffle_options": question.shuffle_options,
                    "dimension_id": pq.dimension_id,
                    "order_num": i + 1,  # 显示顺序
                    "original_order": pq.order_num,  # 原始顺序
                    "parent_case_id": question.parent_case_id
                })
        
        return {
            "paper_id": paper_id,
            "is_shuffled": is_shuffled,
            "questions": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取试卷题目失败: {str(e)}")

@router.post("/import_excel")
def import_questions_from_excel(file: UploadFile = File(...)):
    """
    解析Excel文件，返回题目预览数据，不直接入库。
    Excel格式要求：
    | 题目内容 | 选项A | 选项B | 选项C | 选项D | 题目类型 | 选项乱序 |
    """
    content = file.file.read()
    df = pd.read_excel(io.BytesIO(content))
    questions = []
    option_cols = [col for col in df.columns if re.match(r"选项[ABCD]", str(col))]
    for idx, row in df.iterrows():
        q_content = str(row.get('题目内容', '')).strip()
        q_type = str(row.get('题目类型', 'single')).strip().lower() or 'single'
        shuffle_options = str(row.get('选项乱序', 'False')).strip().lower() in ['true', '1', '是', 'yes']
        options = []
        for col in option_cols:
            opt = str(row.get(col, '')).strip()
            opt = re.sub(r'^[A-D][\.|．、)]\s*', '', opt)
            if opt:
                options.append(opt)
        default_scores = [10, 7, 4, 1] + [0] * (len(options) - 4) if len(options) > 4 else [10, 7, 4, 1][:len(options)]
        questions.append({
            "content": q_content,
            "type": q_type,
            "options": options,
            "scores": default_scores,
            "shuffle_options": shuffle_options
        })
    return {"questions": questions}

@router.post("/import_excel_confirm")
def import_questions_excel_confirm(questions: List[dict] = Body(...), db: Session = Depends(get_db)):
    """
    批量写入题库。
    """
    created = []
    for q in questions:
        question = Question(
            content=q.get('content', ''),
            type=q.get('type', 'single'),
            options=q.get('options', []),
            scores=q.get('scores', []),
            shuffle_options=q.get('shuffle_options', False)
        )
        db.add(question)
        db.flush()  # 获取ID
        created.append({"id": question.id, "content": question.content})
    db.commit()
    return {"created": created, "count": len(created)}

# 试卷相关Excel导入
@paper_router.post("/{paper_id}/import_excel")
def import_paper_questions_from_excel(paper_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    解析Excel文件，返回题目预览数据，不直接入库。
    """
    content = file.file.read()
    df = pd.read_excel(io.BytesIO(content))
    questions = []
    option_cols = [col for col in df.columns if re.match(r"选项[ABCD]", str(col))]
    for idx, row in df.iterrows():
        q_content = str(row.get('题目内容', '')).strip()
        q_type = str(row.get('题目类型', 'single')).strip().lower() or 'single'
        shuffle_options = str(row.get('选项乱序', 'False')).strip().lower() in ['true', '1', '是', 'yes']
        options = []
        for col in option_cols:
            opt = str(row.get(col, '')).strip()
            opt = re.sub(r'^[A-D][\.|．、)]\s*', '', opt)
            if opt:
                options.append(opt)
        default_scores = [10, 7, 4, 1] + [0] * (len(options) - 4) if len(options) > 4 else [10, 7, 4, 1][:len(options)]
        questions.append({
            "content": q_content,
            "type": q_type,
            "options": options,
            "scores": default_scores,
            "shuffle_options": shuffle_options
        })
    return {"questions": questions}

@paper_router.post("/{paper_id}/import_excel_confirm")
def import_paper_questions_excel_confirm(paper_id: int, questions: List[dict] = Body(...), db: Session = Depends(get_db)):
    """
    批量写入试卷。
    """
    created = []
    order_num = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).count() + 1
    for q in questions:
        # 先创建题目
        question = Question(
            content=q.get('content', ''),
            type=q.get('type', 'single'),
            options=q.get('options', []),
            scores=q.get('scores', []),
            shuffle_options=q.get('shuffle_options', False)
        )
        db.add(question)
        db.flush()  # 获取ID
        # 关联到试卷
        pq = PaperQuestion(
            paper_id=paper_id,
            question_id=question.id,
            order_num=order_num
        )
        db.add(pq)
        order_num += 1
        created.append({"id": question.id, "content": question.content})
    db.commit()
    return {"created": created, "count": len(created)}

# 获取单个试卷
@paper_router.get("/{paper_id}")
def get_paper(paper_id: str, db: Session = Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        raise HTTPException(status_code=404, detail="试卷不存在")
    return paper

# 获取用户列表（管理员用）
@app.get("/users", summary="获取用户列表")
def get_users(
    position: str = Query(None, description="岗位"),
    age_min: int = Query(None, description="最小年龄"),
    age_max: int = Query(None, description="最大年龄"),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if position:
        query = query.filter(User.position == position)
    if age_min is not None:
        query = query.filter(User.age >= age_min)
    if age_max is not None:
        query = query.filter(User.age <= age_max)
    users = query.all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "gender": user.gender,
            "age": user.age,
            "position": user.position
        }
        for user in users
    ]

# 被试者管理路由
participant_router = APIRouter(prefix="/participants", tags=["被试者管理"])

# 获取被试者列表
@participant_router.get("/", response_model=List[ParticipantOut])
@participant_router.get("", response_model=List[ParticipantOut])
def get_participants(
    position: str = Query(None, description="岗位"),
    age_min: int = Query(None, description="最小年龄"),
    age_max: int = Query(None, description="最大年龄"),
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.role == UserRole.participant)
    if position:
        query = query.filter(User.position == position)
    if age_min is not None:
        query = query.filter(User.age >= age_min)
    if age_max is not None:
        query = query.filter(User.age <= age_max)
    participants = query.order_by(User.id.desc()).all()
    return participants

# 创建被试者
@participant_router.post("/", response_model=ParticipantOut)
@participant_router.post("", response_model=ParticipantOut)
def create_participant(p: ParticipantCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == p.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user = User(
        username=p.username,
        password_hash=get_password_hash(p.password),
        real_name=p.real_name,
        email=p.email,
        phone=p.phone,
        role=UserRole.participant,
        is_active=p.is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 更新被试者
@participant_router.put("/{participant_id}", response_model=ParticipantOut)
def update_participant(participant_id: int, p: ParticipantUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == participant_id, User.role == UserRole.participant).first()
    if not user:
        raise HTTPException(status_code=404, detail="被试者不存在")
    
    # 如果更新用户名，检查是否重复
    if p.username and p.username != user.username:
        existing_user = db.query(User).filter(User.username == p.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")
    
    for field, value in p.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

# 删除被试者
@participant_router.delete("/{participant_id}")
def delete_participant(participant_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == participant_id, User.role == UserRole.participant).first()
    if not user:
        raise HTTPException(status_code=404, detail="被试者不存在")
    
    db.delete(user)
    db.commit()
    return {"msg": "删除成功"}

# 批量导入被试者
@participant_router.post("/import_excel")
def import_participants_from_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件(.xlsx, .xls)")
    
    try:
        import pandas as pd
        from io import BytesIO
        
        # 读取Excel文件
        content = file.file.read()
        df = pd.read_excel(BytesIO(content))
        
        # 检查必需的列
        required_columns = ['username', 'password', 'real_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Excel文件缺少必需列: {', '.join(missing_columns)}")
        
        # 处理数据
        success_count = 0
        error_messages = []
        
        for index, row in df.iterrows():
            try:
                username = str(row['username']).strip()
                password = str(row['password']).strip()
                real_name = str(row['real_name']).strip()
                email_val = row.get('email')
                email = str(email_val).strip() if email_val is not None and pd.notna(email_val) else None
                phone_val = row.get('phone')
                phone = str(phone_val).strip() if phone_val is not None and pd.notna(phone_val) else None
                is_active_val = row.get('is_active', True)
                is_active = bool(is_active_val) if is_active_val is not None and pd.notna(is_active_val) else True
                
                # 验证数据
                if not username or not password or not real_name:
                    error_messages.append(f"第{str(int(index) + 2)}行: 用户名、密码、真实姓名不能为空")
                    continue
                
                # 检查用户名是否已存在
                existing_user = db.query(User).filter(User.username == username).first()
                if existing_user:
                    error_messages.append(f"第{str(int(index) + 2)}行: 用户名 '{username}' 已存在")
                    continue
                
                # 创建用户
                user = User(
                    username=username,
                    password_hash=get_password_hash(password),
                    real_name=real_name,
                    email=email,
                    phone=phone,
                    role=UserRole.participant,
                    is_active=is_active
                )
                db.add(user)
                success_count += 1
                
            except Exception as e:
                error_messages.append(f"第{str(int(index) + 2)}行: {str(e)}")
        
        db.commit()
        
        return {
            "msg": f"成功导入 {success_count} 个被试者",
            "success_count": success_count,
            "error_count": len(error_messages),
            "errors": error_messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

# 维度路由
dimension_router = APIRouter(prefix="/dimensions", tags=["维度管理"])

# 获取试卷的所有维度
@dimension_router.get("/paper/{paper_id}", response_model=List[DimensionOut])
def get_paper_dimensions(paper_id: int, db: Session = Depends(get_db)):
    """获取试卷的所有维度（树形结构）"""
    try:
        # 获取所有大维度（parent_id为None的）
        major_dimensions = db.query(Dimension).filter(
            Dimension.paper_id == paper_id,
            Dimension.parent_id.is_(None)
        ).order_by(Dimension.order_num).all()
        
        def build_dimension_tree(dimension):
            # 获取子维度
            children = db.query(Dimension).filter(
                Dimension.parent_id == dimension.id
            ).order_by(Dimension.order_num).all()
            
            # 递归构建子维度树
            children_data = [build_dimension_tree(child) for child in children]
            
            return DimensionOut(
                id=dimension.id,
                paper_id=dimension.paper_id,
                parent_id=dimension.parent_id,
                name=dimension.name,
                description=dimension.description,
                weight=dimension.weight,
                order_num=dimension.order_num,
                created_at=dimension.created_at,
                updated_at=dimension.updated_at,
                children=children_data
            )
        
        result = [build_dimension_tree(dim) for dim in major_dimensions]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取维度失败: {str(e)}")

# 创建维度
@dimension_router.post("/", response_model=DimensionOut)
def create_dimension(dimension: DimensionCreate, db: Session = Depends(get_db)):
    """创建维度"""
    try:
        # 检查试卷是否存在
        paper = db.query(Paper).filter(Paper.id == dimension.paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 如果指定了父维度，检查父维度是否存在
        if dimension.parent_id:
            parent = db.query(Dimension).filter(Dimension.id == dimension.parent_id).first()
            if not parent:
                raise HTTPException(status_code=404, detail="父维度不存在")
        
        new_dimension = Dimension(
            paper_id=dimension.paper_id,
            parent_id=dimension.parent_id,
            name=dimension.name,
            description=dimension.description,
            weight=dimension.weight,
            order_num=dimension.order_num
        )
        
        db.add(new_dimension)
        db.commit()
        db.refresh(new_dimension)
        
        return new_dimension
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建维度失败: {str(e)}")

# 更新维度
@dimension_router.put("/{dimension_id}", response_model=DimensionOut)
def update_dimension(dimension_id: int, dimension: DimensionUpdate, db: Session = Depends(get_db)):
    """更新维度"""
    try:
        db_dimension = db.query(Dimension).filter(Dimension.id == dimension_id).first()
        if not db_dimension:
            raise HTTPException(status_code=404, detail="维度不存在")
        
        for field, value in dimension.dict(exclude_unset=True).items():
            setattr(db_dimension, field, value)
        
        db.commit()
        db.refresh(db_dimension)
        return db_dimension
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新维度失败: {str(e)}")

# 删除维度
@dimension_router.delete("/{dimension_id}")
def delete_dimension(dimension_id: int, db: Session = Depends(get_db)):
    """删除维度"""
    try:
        db_dimension = db.query(Dimension).filter(Dimension.id == dimension_id).first()
        if not db_dimension:
            raise HTTPException(status_code=404, detail="维度不存在")
        
        # 检查是否有子维度
        children = db.query(Dimension).filter(Dimension.parent_id == dimension_id).count()
        if children > 0:
            raise HTTPException(status_code=400, detail="无法删除包含子维度的维度，请先删除子维度")
        
        # 检查是否有关联的题目
        questions_count = db.query(Question).filter(Question.dimension_id == dimension_id).count()
        if questions_count > 0:
            raise HTTPException(status_code=400, detail="无法删除包含题目的维度，请先移除题目")
        
        db.delete(db_dimension)
        db.commit()
        return {"msg": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除维度失败: {str(e)}")

# 获取维度可匹配的题目
@dimension_router.get("/{dimension_id}/available-questions")
def get_available_questions_for_dimension(dimension_id: int, paper_id: int, db: Session = Depends(get_db)):
    """获取维度可匹配的题目（已匹配的题目不显示，有子维度的父维度不能匹配）"""
    try:
        # 检查维度是否存在且属于该试卷
        dimension = db.query(Dimension).filter(
            Dimension.id == dimension_id,
            Dimension.paper_id == paper_id
        ).first()
        if not dimension:
            raise HTTPException(status_code=404, detail="维度不存在")
        
        # 检查该维度是否有子维度，如果有则不允许匹配题目
        children_count = db.query(Dimension).filter(Dimension.parent_id == dimension_id).count()
        if children_count > 0:
            raise HTTPException(status_code=400, detail="该维度有子维度，请为子维度匹配题目")
        
        # 获取试卷中所有题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
        paper_question_ids = [pq.question_id for pq in paper_questions]
        
        # 获取已匹配的题目ID（包括所有维度的已匹配题目）
        matched_questions = db.query(Question.id).filter(
            Question.dimension_id.isnot(None)
        ).all()
        matched_ids = [q[0] for q in matched_questions]
        
        # 获取可匹配的题目（在试卷中但未匹配的）
        available_questions = db.query(Question).filter(
            Question.id.in_(paper_question_ids),
            ~Question.id.in_(matched_ids)
        ).all()
        
        return [
            {
                "id": q.id,
                "content": q.content,
                "type": q.type,
                "options": q.options,
                "scores": q.scores
            }
            for q in available_questions
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取可匹配题目失败: {str(e)}")

# 匹配题目到维度
@dimension_router.post("/{dimension_id}/match-questions")
def match_questions_to_dimension(dimension_id: int, request: QuestionIdsRequest, db: Session = Depends(get_db)):
    """匹配题目到维度"""
    try:
        # 检查维度是否存在
        dimension = db.query(Dimension).filter(Dimension.id == dimension_id).first()
        if not dimension:
            raise HTTPException(status_code=404, detail="维度不存在")
        
        # 检查该维度是否有子维度，如果有则不允许匹配题目
        children_count = db.query(Dimension).filter(Dimension.parent_id == dimension_id).count()
        if children_count > 0:
            raise HTTPException(status_code=400, detail="该维度有子维度，请为子维度匹配题目")
        
        # 检查题目是否已被其他维度匹配
        for question_id in request.question_ids:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question and question.dimension_id is not None:
                raise HTTPException(status_code=400, detail=f"题目ID {question_id} 已被其他维度匹配")
        
        # 更新题目的维度ID（同时更新questions表和paper_questions表）
        updated_count = 0
        for question_id in request.question_ids:
            # 更新questions表
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                question.dimension_id = dimension_id
                updated_count += 1
            
            # 同时更新paper_questions表中该题目的维度ID
            paper_questions = db.query(PaperQuestion).filter(PaperQuestion.question_id == question_id).all()
            for pq in paper_questions:
                pq.dimension_id = dimension_id
        
        db.commit()
        return {"msg": f"成功匹配 {updated_count} 道题目到维度"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匹配题目失败: {str(e)}")

# 获取维度已匹配的题目
@dimension_router.get("/{dimension_id}/matched-questions")
def get_matched_questions_for_dimension(dimension_id: int, db: Session = Depends(get_db)):
    """获取该维度已匹配的题目列表"""
    try:
        questions = db.query(Question).filter(Question.dimension_id == dimension_id).all()
        return [
            {
                "id": q.id,
                "content": q.content,
                "type": q.type,
                "options": q.options,
                "scores": q.scores
            }
            for q in questions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取已匹配题目失败: {str(e)}")

# 移除题目与维度的归属
@dimension_router.post("/{dimension_id}/remove-question")
def remove_question_from_dimension(dimension_id: int, question_id: int = Body(...), db: Session = Depends(get_db)):
    """将题目的dimension_id设为null"""
    try:
        question = db.query(Question).filter(Question.id == question_id, Question.dimension_id == dimension_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="题目不存在或不属于该维度")
        
        # 同时更新questions表和paper_questions表
        question.dimension_id = None
        
        # 更新paper_questions表中该题目的维度ID
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.question_id == question_id).all()
        for pq in paper_questions:
            pq.dimension_id = None
        
        db.commit()
        return {"msg": "移除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除题目失败: {str(e)}")

# 注册试卷路由
app.include_router(paper_router)

# 注册维度路由
app.include_router(dimension_router)

# 仪表盘统计API
@app.get("/dashboard/stats", summary="获取仪表盘统计数据")
def get_dashboard_stats(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    try:
        # 总被试者数（参与者角色）
        total_participants = db.query(User).filter(User.role == UserRole.participant).count()
        
        # 题库题目数
        total_questions = db.query(Question).count()
        
        # 试卷总数
        total_papers = db.query(Paper).count()
        
        # 已生成报告数（完成的试卷分配）
        completed_reports = db.query(PaperAssignment).filter(PaperAssignment.status == "completed").count()
        
        # 计算平均得分（这里需要根据实际业务逻辑调整）
        # 暂时返回一个模拟值，实际应该从答题记录中计算
        avg_score = 78.5  # 这个值需要根据实际的答题记录计算
        
        return {
            "total_participants": total_participants,
            "total_questions": total_questions,
            "total_papers": total_papers,
            "completed_reports": completed_reports,
            "avg_score": avg_score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@app.get("/dashboard/recent-assessments", summary="获取最近测评数据")
def get_recent_assessments(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db), limit: int = 10):
    """获取最近的测评数据"""
    try:
        from sqlalchemy.orm import selectinload
        recent_assignments = db.query(PaperAssignment).options(
            selectinload(PaperAssignment.user),
            selectinload(PaperAssignment.paper)
        ).filter(
            PaperAssignment.status == "completed"
        ).order_by(
            PaperAssignment.completed_at.desc()
        ).limit(limit).all()
        result = []
        for assignment in recent_assignments:
            # 真实总分
            score_info = calculate_user_paper_score(db, assignment.paper_id, assignment.user_id)
            score = score_info["total_score"] if score_info else 0
            result.append({
                "id": assignment.id,
                "name": assignment.user.real_name if assignment.user.real_name else assignment.user.username,
                "score": score,
                "date": assignment.completed_at.strftime("%Y-%m-%d %H:%M:%S") if assignment.completed_at else None,
                "paper_name": assignment.paper.name
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近测评数据失败: {str(e)}")

# ========== 仪表盘统计图表接口 ========== #

@app.get("/dashboard/paper-completion", summary="获取所有试卷的完成量")
def get_paper_completion(db: Session = Depends(get_db)):
    papers = db.query(Paper).all()
    result = []
    for paper in papers:
        assigned_count = db.query(PaperAssignment).filter(
            PaperAssignment.paper_id == paper.id
        ).count()
        completed_count = db.query(PaperAssignment).filter(
            PaperAssignment.paper_id == paper.id,
            PaperAssignment.status == "completed"
        ).count()
        result.append({
            "paper_id": paper.id,
            "paper_name": paper.name,
            "assigned_count": assigned_count,
            "completed_count": completed_count
        })
    return result

@app.get("/dashboard/paper-dimension-avg", summary="获取某试卷所有小维度的平均分")
def get_paper_dimension_avg(paper_id: int, db: Session = Depends(get_db)):
    # 获取所有小维度（parent_id不为None，或无子维度的维度）
    all_dims = db.query(Dimension).filter(Dimension.paper_id == paper_id).order_by(Dimension.order_num).all()
    # 先找所有有parent_id的小维度
    small_dims = [d for d in all_dims if d.parent_id is not None]
    # 再找没有子维度的父维度（即叶子节点）
    parent_ids = set(d.parent_id for d in all_dims if d.parent_id is not None)
    leaf_big_dims = [d for d in all_dims if d.parent_id is None and d.id not in parent_ids]
    dims = small_dims + leaf_big_dims
    result = []
    for dim in dims:
        # 查询所有相关题目
        questions = db.query(Question).filter(Question.dimension_id == dim.id).all()
        question_ids = [q.id for q in questions]
        if not question_ids:
            avg_score = 0
        else:
            from sqlalchemy import text
            answers = db.execute(
                text("SELECT score FROM answers WHERE question_id IN :qids"),
                {"qids": tuple(question_ids)}
            ).fetchall()
            scores = [row[0] for row in answers if row[0] is not None]
            # 分数区间归一化到[0,10]，假设原始分数最大为10
            avg_score = round(min(10, max(0, sum(scores)/len(scores))) if scores else 0, 2)
        result.append({
            "dimension_name": dim.name,
            "avg_score": avg_score
        })
    return result

@app.get("/dashboard/paper-dimension-avg-grouped", summary="获取某试卷分组（大维度-小维度）下的所有小维度平均分")
def get_paper_dimension_avg_grouped(paper_id: int, db: Session = Depends(get_db)):
    """
    返回结构：
    {
      "groups": [
        {
          "group_name": "大维度A",
          "dimensions": [
            {"dimension_name": "小维度1", "avg_score": 8.5},
            ...
          ]
        },
        ...
      ]
    }
    """
    # 获取所有大维度（parent_id=None，按order_num排序）
    big_dims = db.query(Dimension).filter(Dimension.paper_id == paper_id, Dimension.parent_id == None).order_by(Dimension.order_num).all()
    # 获取所有小维度（parent_id!=None，按order_num排序）
    small_dims = db.query(Dimension).filter(Dimension.paper_id == paper_id, Dimension.parent_id != None).order_by(Dimension.order_num).all()
    # 以大维度id分组
    big_dim_map = {d.id: d for d in big_dims}
    group_list = []
    for big in big_dims:
        group = {"group_name": big.name, "dimensions": []}
        # 找到该大维度下所有小维度
        children = [d for d in small_dims if d.parent_id == big.id]
        # 如果没有小维度，视为叶子大维度
        if not children:
            children = [big]
        for dim in children:
            # 查询所有相关题目
            questions = db.query(Question).filter(Question.dimension_id == dim.id).all()
            question_ids = [q.id for q in questions]
            if not question_ids:
                avg_score = 0
            else:
                from sqlalchemy import text
                answers = db.execute(
                    text("SELECT score FROM answers WHERE question_id IN :qids"),
                    {"qids": tuple(question_ids)}
                ).fetchall()
                scores = [row[0] for row in answers if row[0] is not None]
                avg_score = round(min(10, max(0, sum(scores)/len(scores))) if scores else 0, 2)
            group["dimensions"].append({
                "dimension_name": dim.name,
                "avg_score": avg_score
            })
        group_list.append(group)
    return {"groups": group_list}

# 注册被试者路由
app.include_router(participant_router)

# 注册路由
app.include_router(router)

# ========== 新增：注册报告API ========== #
from app.api import report_api
app.include_router(report_api.router)

# ========== 测试结果API ========== #

class ScoreDetail(BaseModel):
    name: str
    score: float
    sub_dimensions: Optional[List['ScoreDetail']] = None

class UserResult(BaseModel):
    user_id: int
    user_name: str
    total_score: float
    big_dimensions: List[ScoreDetail]

class PaperResult(BaseModel):
    paper_id: int
    paper_name: str
    total_score: float
    big_dimensions: List[ScoreDetail]

ScoreDetail.update_forward_refs()

# 算分核心函数

def calculate_user_paper_score(db, paper_id, user_id):
    print(f"开始计算用户 {user_id} 试卷 {paper_id} 的分数...")
    
    # 1. 获取所有题目-维度映射
    paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == paper_id).all()
    question_dim_map = {}
    for pq in paper_questions:
        question_dim_map[pq.question_id] = pq.dimension_id
    
    print(f"试卷题目数量: {len(paper_questions)}")
    print(f"题目-维度映射: {question_dim_map}")

    # 2. 获取所有维度（大/小）
    all_dimensions = db.query(Dimension).filter(Dimension.paper_id == paper_id).all()
    dim_map = {d.id: d for d in all_dimensions}
    big_dims = [d for d in all_dimensions if d.parent_id is None]
    small_dims = [d for d in all_dimensions if d.parent_id is not None]
    
    print(f"维度总数: {len(all_dimensions)}, 大维度: {len(big_dims)}, 小维度: {len(small_dims)}")

    # 3. 获取所有题目分数
    questions = db.query(Question).filter(Question.id.in_(question_dim_map.keys())).all()
    question_score_map = {q.id: q.scores for q in questions}
    
    print(f"题目数量: {len(questions)}")
    print(f"题目分数映射: {question_score_map}")

    # 4. 获取被试者答题记录
    try:
        from sqlalchemy import text
        question_ids = list(question_dim_map.keys())
        if not question_ids:
            print("没有找到试卷题目")
            answer_map = {}
        else:
            # 使用 SQLAlchemy 的 text() 函数
            query = text("SELECT question_id, answer, score FROM answers WHERE user_id = :user_id AND question_id IN :qids")
            answers = db.execute(query, {"user_id": user_id, "qids": tuple(question_ids)}).fetchall()
            answer_map = {row[0]: row[1] for row in answers}
            print(f"查询到的答题记录数量: {len(answers)}")
            print(f"答题记录: {answer_map}")
    except Exception as e:
        print(f"查询答题记录失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        answer_map = {}

    # 5. 统计每个小维度得分
    small_dim_scores = defaultdict(list)  # {dim_id: [得分, ...]}
    print(f"\n开始计算各维度得分...")
    
    for qid, dim_id in question_dim_map.items():
        if dim_id is None:
            print(f"题目 {qid} 没有对应维度，跳过")
            continue
        
        # 找到该题的答题情况
        ans = answer_map.get(qid)
        if ans is None:
            print(f"题目 {qid} 没有答题记录")
            continue
        
        print(f"题目 {qid} (维度 {dim_id}): 答案={ans}, 类型={type(ans)}")
        
        # 题目分数
        q_scores = question_score_map.get(qid, [10,7,4,1])
        print(f"  题目分数设置: {q_scores}")
        
        # 解析答案
        idx = None
        if isinstance(ans, str):
            try:
                # 尝试解析JSON字符串
                import json
                parsed_ans = json.loads(ans)
                if isinstance(parsed_ans, list) and len(parsed_ans) > 0:
                    if isinstance(parsed_ans[0], int):
                        idx = parsed_ans[0]
                    elif isinstance(parsed_ans[0], str):
                        idx = ord(parsed_ans[0].upper()) - ord('A')
                print(f"  解析JSON后: {parsed_ans}, 索引: {idx}")
            except:
                # 直接解析字符串
                idx = ord(ans.upper()) - ord('A')
                print(f"  直接解析字符串: {ans}, 索引: {idx}")
        elif isinstance(ans, list) and len(ans) > 0:
            if isinstance(ans[0], int):
                idx = ans[0]
            elif isinstance(ans[0], str):
                idx = ord(ans[0].upper()) - ord('A')
            print(f"  直接解析列表: {ans}, 索引: {idx}")
        
        if idx is not None and 0 <= idx < len(q_scores):
            score = q_scores[idx]
            small_dim_scores[dim_id].append(score)
            print(f"  ✅ 得分: {score}")
        else:
            print(f"  ❌ 无效索引: {idx}, 分数范围: 0-{len(q_scores)-1}")

    # 6. 计算小维度平均分
    small_dim_avg = {}
    for dim in small_dims:
        scores = small_dim_scores.get(dim.id, [])
        avg = round(sum(scores)/len(scores), 2) if scores else 0.0
        small_dim_avg[dim.id] = avg

    # 7. 计算大维度平均分
    big_dim_avg = {}
    big_dim_detail = []
    for big in big_dims:
        sub_dims = [d for d in small_dims if d.parent_id == big.id]
        sub_scores = [small_dim_avg[d.id] for d in sub_dims]
        avg = round(sum(sub_scores)/len(sub_scores), 2) if sub_scores else 0.0
        big_dim_avg[big.id] = avg
        big_dim_detail.append(ScoreDetail(
            name=big.name,
            score=avg,
            sub_dimensions=[ScoreDetail(name=d.name, score=small_dim_avg[d.id]) for d in sub_dims]
        ))

    # 8. 计算全卷平均分
    all_scores = []
    for scores in small_dim_scores.values():
        all_scores.extend(scores)
    total_score = round(sum(all_scores)/len(all_scores), 2) if all_scores else 0.0

    return {
        "total_score": total_score,
        "big_dimensions": big_dim_detail
    }

# ========== API实现 ========== #

@app.get("/results/by-paper", response_model=List[UserResult], summary="按试卷查看测试结果")
def get_results_by_paper(paper_id: int = Query(..., description="试卷ID"), token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    # 获取所有已完成该试卷的被试者
    assignments = db.query(PaperAssignment).filter(
        PaperAssignment.paper_id == paper_id,
        PaperAssignment.status == "completed"
    ).all()
    results = []
    for a in assignments:
        user = db.query(User).filter(User.id == a.user_id).first()
        score_info = calculate_user_paper_score(db, paper_id, a.user_id)
        results.append(UserResult(
            user_id=user.id,
            user_name=user.real_name or user.username,
            total_score=score_info["total_score"],
            big_dimensions=score_info["big_dimensions"]
        ))
    return results

@app.get("/results/by-user", response_model=List[PaperResult], summary="按被试者查看测试结果")
def get_results_by_user(user_id: int = Query(..., description="用户ID"), token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    # 获取该被试者已完成的所有试卷
    assignments = db.query(PaperAssignment).filter(
        PaperAssignment.user_id == user_id,
        PaperAssignment.status == "completed"
    ).all()
    results = []
    for a in assignments:
        paper = db.query(Paper).filter(Paper.id == a.paper_id).first()
        score_info = calculate_user_paper_score(db, a.paper_id, user_id)
        results.append(PaperResult(
            paper_id=paper.id,
            paper_name=paper.name,
            total_score=score_info["total_score"],
            big_dimensions=score_info["big_dimensions"]
        ))
    return results

@app.get("/results/detail", summary="获取单个被试者单份试卷的详细分数")
def get_result_detail(paper_id: int = Query(...), user_id: int = Query(...), token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    # 获取该被试者在该试卷的详细分数
    try:
        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取试卷信息
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            raise HTTPException(status_code=404, detail="试卷不存在")
        
        # 计算分数
        score_data = calculate_user_paper_score(db, paper_id, user_id)
        
        return {
            "user_id": user_id,
            "user_name": user.real_name or user.username,
            "paper_id": paper_id,
            "paper_name": paper.name,
            "total_score": score_data["total_score"],
            "dimensions": score_data["dimensions"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取详细分数失败: {str(e)}")

# 报告相关模型
class ReportOut(BaseModel):
    id: int
    user_id: int
    user_name: str
    paper_id: int
    paper_name: str
    file_path: str
    file_name: str
    file_size: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        orm_mode = True

class ReportListResponse(BaseModel):
    reports: List[ReportOut]
    total: int
    page: int
    page_size: int

class BatchDeleteRequest(BaseModel):
    report_ids: List[int]

# 报告管理API
@app.get("/reports", response_model=ReportListResponse, summary="获取报告列表")
def get_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户ID筛选"),
    paper_id: int = Query(None, description="试卷ID筛选"),
    status: str = Query(None, description="状态筛选"),
    position: str = Query(None, description="岗位"),
    age_min: int = Query(None, description="最小年龄"),
    age_max: int = Query(None, description="最大年龄"),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    query = db.query(Report).join(User, Report.user_id == User.id)
    if user_id:
        query = query.filter(Report.user_id == user_id)
    if paper_id:
        query = query.filter(Report.paper_id == paper_id)
    if status:
        query = query.filter(Report.status == status)
    if position:
        query = query.filter(User.position == position)
    if age_min is not None:
        query = query.filter(User.age >= age_min)
    if age_max is not None:
        query = query.filter(User.age <= age_max)
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    # ... 保持原有返回结构 ...
    report_list = []
    for report in reports:
        user = report.user
        paper = report.paper
        report_list.append({
            "id": report.id,
            "user_id": report.user_id,
            "user_name": user.real_name if user else None,
            "paper_id": report.paper_id,
            "paper_name": paper.name if paper else None,
            "file_path": report.file_path,
            "file_name": report.file_name,
            "file_size": report.file_size,
            "status": report.status,
            "error_message": report.error_message,
            "created_at": report.created_at,
            "gender": user.gender if user else None,
            "age": user.age if user else None,
            "position": user.position if user else None
        })
    return ReportListResponse(reports=report_list, total=total, page=page, page_size=page_size)

@app.delete("/reports/{report_id}", summary="删除单个报告")
def delete_report(
    report_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """删除单个报告"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 删除文件
        import os
        if os.path.exists(report.file_path):
            os.remove(report.file_path)
        
        # 删除数据库记录
        db.delete(report)
        db.commit()
        
        return {"message": "报告删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除报告失败: {str(e)}")

@app.delete("/reports/batch", summary="批量删除报告")
def batch_delete_reports(
    request: BatchDeleteRequest,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """批量删除报告"""
    try:
        reports = db.query(Report).filter(Report.id.in_(request.report_ids)).all()
        
        if not reports:
            raise HTTPException(status_code=404, detail="未找到要删除的报告")
        
        # 删除文件
        import os
        deleted_count = 0
        for report in reports:
            if os.path.exists(report.file_path):
                os.remove(report.file_path)
            db.delete(report)
            deleted_count += 1
        
        db.commit()
        
        return {"message": f"成功删除 {deleted_count} 个报告"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量删除报告失败: {str(e)}")

@app.get("/reports/{report_id}/download", summary="下载报告")
def download_report(
    report_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """下载报告文件"""
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        if report.status != "completed":
            raise HTTPException(status_code=400, detail="报告尚未生成完成")
        
        import os
        if not os.path.exists(report.file_path):
            raise HTTPException(status_code=404, detail="报告文件不存在")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=report.file_path,
            filename=report.file_name,
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")

@app.post("/reports/{report_id}/download", summary="批量下载报告")
def batch_download_reports(
    report_ids: List[int] = Body(...),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """批量下载报告（返回下载链接列表）"""
    try:
        reports = db.query(Report).filter(Report.id.in_(report_ids)).all()
        
        if not reports:
            raise HTTPException(status_code=404, detail="未找到要下载的报告")
        
        download_links = []
        for report in reports:
            if report.status == "completed":
                download_links.append({
                    "report_id": report.id,
                    "file_name": report.file_name,
                    "download_url": f"/api/reports/{report.id}/download"
                })
        
        return {
            "message": f"找到 {len(download_links)} 个可下载的报告",
            "download_links": download_links
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量下载报告失败: {str(e)}")



@app.post("/assignments/{assignment_id}/generate-question-order", summary="为用户生成个人题目顺序")
def generate_user_question_order(
    assignment_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """为用户生成个人的题目顺序（基于试卷的乱序设置）"""
    try:
        # 获取试卷分配信息
        assignment = db.query(PaperAssignment).filter(PaperAssignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="试卷分配不存在")
        
        # 获取试卷题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == assignment.paper_id).all()
        
        if not paper_questions:
            raise HTTPException(status_code=400, detail="试卷没有题目")
        
        # 检查是否启用乱序
        is_shuffled = paper_questions[0].is_shuffled if paper_questions else False
        
        if is_shuffled:
            # 如果试卷启用乱序，为用户生成个人顺序
            import random
            
            # 使用用户ID作为种子，确保同一用户每次得到相同顺序
            random.seed(assignment.user_id)
            
            # 获取题目ID列表
            question_ids = [pq.question_id for pq in paper_questions]
            
            # 生成个人顺序
            personal_order = question_ids.copy()
            random.shuffle(personal_order)
            
            # 保存到数据库
            assignment.question_order = personal_order
            db.commit()
            
            return {
                "message": "个人题目顺序已生成",
                "user_id": assignment.user_id,
                "question_count": len(question_ids),
                "question_order": personal_order
            }
        else:
            # 如果试卷未启用乱序，使用原始顺序
            question_ids = [pq.question_id for pq in sorted(paper_questions, key=lambda x: x.order_num)]
            assignment.question_order = question_ids
            db.commit()
            
            return {
                "message": "使用原始题目顺序",
                "user_id": assignment.user_id,
                "question_count": len(question_ids),
                "question_order": question_ids
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成题目顺序失败: {str(e)}")

# 选项乱序相关API
@app.post("/assignments/{assignment_id}/generate-option-orders", summary="为用户生成选项顺序")
def generate_user_option_orders(
    assignment_id: int,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    """为用户生成选项顺序（基于题目的选项乱序设置）"""
    try:
        # 获取试卷分配信息
        assignment = db.query(PaperAssignment).filter(PaperAssignment.id == assignment_id).first()
        if not assignment:
            raise HTTPException(status_code=404, detail="试卷分配不存在")
        
        # 获取试卷题目
        paper_questions = db.query(PaperQuestion).filter(PaperQuestion.paper_id == assignment.paper_id).all()
        
        if not paper_questions:
            raise HTTPException(status_code=400, detail="试卷没有题目")
        
        # 获取所有题目详情
        question_ids = [pq.question_id for pq in paper_questions]
        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        
        # 生成选项顺序
        import random
        option_orders = {}
        
        for question in questions:
            if question.shuffle_options and question.options:
                # 使用用户ID和题目ID作为种子，确保同一用户同一题目每次得到相同顺序
                random.seed(assignment.user_id + question.id)
                
                # 生成选项索引顺序
                option_indices = list(range(len(question.options)))
                random.shuffle(option_indices)
                
                option_orders[question.id] = option_indices
            else:
                # 不启用选项乱序，使用原始顺序
                option_orders[question.id] = list(range(len(question.options)))
        
        # 保存到数据库
        assignment.option_orders = option_orders
        db.commit()
        
        return {
            "message": "选项顺序已生成",
            "user_id": assignment.user_id,
            "question_count": len(questions),
            "option_orders": option_orders
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"生成选项顺序失败: {str(e)}")

# ====== RedoRequest ORM模型 ======
class RedoRequest(Base):
    __tablename__ = "redo_requests"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("paper_assignments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    request_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending, processed
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 处理人
    process_time = Column(DateTime)
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    paper = relationship("Paper", foreign_keys=[paper_id])
    assignment = relationship("PaperAssignment", foreign_keys=[assignment_id])
    admin = relationship("User", foreign_keys=[admin_id])

# ====== RedoRequest Pydantic模型 ======
class RedoRequestCreate(BaseModel):
    assignment_id: int

class RedoRequestOut(BaseModel):
    id: int
    assignment_id: int
    user_id: int
    paper_id: int
    request_time: datetime
    status: str
    admin_id: int | None = None
    process_time: datetime | None = None
    user_name: str | None = None
    paper_name: str | None = None
    class Config:
        orm_mode = True

# ... existing code ...
# ====== Redo相关API ======
from fastapi import Security

@app.post("/redo-request", summary="被试者申请重做")
def create_redo_request(
    req: RedoRequestCreate,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    assignment = db.query(PaperAssignment).filter(PaperAssignment.id == req.assignment_id, PaperAssignment.user_id == user.id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="试卷分配不存在")
    # 检查是否已申请过且未处理
    exist = db.query(RedoRequest).filter(RedoRequest.assignment_id == req.assignment_id, RedoRequest.status == "pending").first()
    if exist:
        raise HTTPException(status_code=400, detail="已申请重做，等待管理员处理")
    redo = RedoRequest(
        assignment_id=req.assignment_id,
        user_id=user.id,
        paper_id=assignment.paper_id
    )
    db.add(redo)
    db.commit()
    db.refresh(redo)
    return {"msg": "重做申请已提交"}

@app.get("/redo-requests", response_model=List[RedoRequestOut], summary="管理员获取所有重做申请")
def get_redo_requests(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=403, detail="无权限")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    requests = db.query(RedoRequest).filter(RedoRequest.status == "pending").order_by(RedoRequest.request_time.desc()).all()
    result = []
    for r in requests:
        user = db.query(User).filter(User.id == r.user_id).first()
        paper = db.query(Paper).filter(Paper.id == r.paper_id).first()
        result.append(RedoRequestOut(
            id=r.id,
            assignment_id=r.assignment_id,
            user_id=r.user_id,
            paper_id=r.paper_id,
            request_time=r.request_time,
            status=r.status,
            admin_id=r.admin_id,
            process_time=r.process_time,
            user_name=user.real_name if user else None,
            paper_name=paper.name if paper else None
        ))
    return result

@app.post("/redo-request/assign", summary="管理员处理单个重做申请并重新分配")
def process_redo_request(
    request_id: int = Body(..., embed=True),
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=403, detail="无权限")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    redo = db.query(RedoRequest).filter(RedoRequest.id == request_id, RedoRequest.status == "pending").first()
    if not redo:
        raise HTTPException(status_code=404, detail="重做申请不存在或已处理")
    # 重新分配试卷（重置assignment状态）
    assignment = db.query(PaperAssignment).filter(PaperAssignment.id == redo.assignment_id).first()
    if assignment:
        assignment.status = "assigned"
        assignment.started_at = None
        assignment.completed_at = None
        db.commit()
    redo.status = "processed"
    redo.admin_id = db.query(User).filter(User.username == username).first().id
    redo.process_time = datetime.utcnow()
    db.commit()
    return {"msg": "已重新分配"}

@app.post("/redo-request/assign-all", summary="管理员一键全部重新分配")
def process_all_redo_requests(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=403, detail="无权限")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token校验失败")
    admin_id = db.query(User).filter(User.username == username).first().id
    requests = db.query(RedoRequest).filter(RedoRequest.status == "pending").all()
    for redo in requests:
        assignment = db.query(PaperAssignment).filter(PaperAssignment.id == redo.assignment_id).first()
        if assignment:
            assignment.status = "assigned"
            assignment.started_at = None
            assignment.completed_at = None
        redo.status = "processed"
        redo.admin_id = admin_id
        redo.process_time = datetime.utcnow()
    db.commit()
    return {"msg": "全部已重新分配"}
#// ... existing code ...


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 