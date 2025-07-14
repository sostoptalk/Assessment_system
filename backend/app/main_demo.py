from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from typing import List
import sys
import os
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
from app.main import get_db, Paper, PaperAssignment, User, PaperOut, participant_router, dimension_router, router

app = FastAPI()
paper_router = APIRouter(prefix="/papers", tags=["试卷管理"])

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssignmentOut(BaseModel):
    id: int
    user_id: int
    user_name: str

@paper_router.get("/{paper_id}/list-assignment", response_model=List[AssignmentOut])
@paper_router.get("/{paper_id}/list-assignment/", response_model=List[AssignmentOut])
def get_paper_assignments(paper_id: str, db=Depends(get_db)):
    paper_id_int = int(paper_id)
    paper = db.query(Paper).filter(Paper.id == paper_id_int).first()
    if not paper:
        return []
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
            })
    return result

@paper_router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: str, db=Depends(get_db)):
    paper = db.query(Paper).filter(Paper.id == int(paper_id)).first()
    if not paper:
        return {"id": int(paper_id), "name": "not found"}
    return paper

@paper_router.get("/{paper_id}/questions")
def get_paper_questions(paper_id: str, db=Depends(get_db)):
    return {"msg": f"paper_id={paper_id} questions"}

@app.get("/dashboard/stats")
def get_dashboard_stats():
    return {"msg": "dashboard stats"}

@app.get("/dashboard/recent-assessments")
def get_recent_assessments():
    return {"msg": "recent assessments"}

@app.get("/results/by-paper")
def get_results_by_paper():
    return {"msg": "results by paper"}

@app.get("/results/by-user")
def get_results_by_user():
    return {"msg": "results by user"}

@app.get("/results/detail")
def get_result_detail():
    return {"msg": "result detail"}

app.include_router(paper_router)
app.include_router(participant_router)
app.include_router(dimension_router)
app.include_router(router)