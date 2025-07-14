#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

db_url = "mysql+pymysql://root:Yrui2997@localhost:3306/test_assessment?charset=utf8mb4"
engine = create_engine(db_url, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(20), nullable=False)
    options = Column(Text, nullable=False)
    scores = Column(Text, nullable=False)
    dimension_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)

class Dimension(Base):
    __tablename__ = "dimensions"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)
    order_num = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaperQuestion(Base):
    __tablename__ = "paper_questions"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    dimension_id = Column(Integer, ForeignKey("dimensions.id"), nullable=True)
    order_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def fix_paper_questions_dimensions():
    """修复paper_questions表的dimension_id"""
    db = next(get_db())
    
    print("============================================================")
    print("修复paper_questions表的dimension_id")
    print("============================================================")
    
    try:
        # 获取所有paper_questions记录
        paper_questions = db.query(PaperQuestion).all()
        print(f"找到 {len(paper_questions)} 条paper_questions记录")
        
        updated_count = 0
        for pq in paper_questions:
            # 获取对应的question
            question = db.query(Question).filter(Question.id == pq.question_id).first()
            if question and question.dimension_id is not None:
                # 如果question有dimension_id，同步到paper_question
                if pq.dimension_id != question.dimension_id:
                    print(f"更新题目 {pq.question_id}: {pq.dimension_id} -> {question.dimension_id}")
                    pq.dimension_id = question.dimension_id
                    updated_count += 1
            elif question and question.dimension_id is None:
                # 如果question没有dimension_id，设置为None
                if pq.dimension_id is not None:
                    print(f"清除题目 {pq.question_id} 的维度: {pq.dimension_id} -> None")
                    pq.dimension_id = None
                    updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"✅ 成功更新 {updated_count} 条记录")
        else:
            print("✅ 所有记录都已同步，无需更新")
        
        # 验证修复结果
        print("\n验证修复结果:")
        paper_questions_after = db.query(PaperQuestion).filter(PaperQuestion.paper_id == 10).all()
        print(f"试卷10的题目数量: {len(paper_questions_after)}")
        
        dimension_counts = {}
        for pq in paper_questions_after:
            if pq.dimension_id is not None:
                dimension_counts[pq.dimension_id] = dimension_counts.get(pq.dimension_id, 0) + 1
        
        print("各维度的题目数量:")
        for dim_id, count in dimension_counts.items():
            dimension = db.query(Dimension).filter(Dimension.id == dim_id).first()
            if dimension:
                print(f"  维度 {dim_id} ({dimension.name}): {count} 题")
        
        null_count = sum(1 for pq in paper_questions_after if pq.dimension_id is None)
        print(f"  未分配维度: {null_count} 题")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_paper_questions_dimensions() 