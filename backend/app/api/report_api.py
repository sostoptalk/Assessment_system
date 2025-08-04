import os
import threading
import time
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# 从main中只导入SessionLocal
from app.main import SessionLocal
from app.api.report_generator import generate_report_task

router = APIRouter(prefix="/reports", tags=["报告生成"])

report_tasks: Dict[str, dict] = {}

class BatchGenerateRequest(BaseModel):
    paper_id: int
    user_ids: List[int]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/batch-generate")
def batch_generate_reports(req: BatchGenerateRequest):
    print(f"[DEBUG] 批量生成报告请求: paper_id={req.paper_id}, user_ids={req.user_ids}")
    task_ids = []
    for user_id in req.user_ids:
        task_id = f"{user_id}_{req.paper_id}_{uuid.uuid4().hex[:8]}"
        print(f"[DEBUG] 创建任务: task_id={task_id}, user_id={user_id}, paper_id={req.paper_id}")
        report_tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "file_path": None,
            "error_message": None,
            "user_id": user_id,
            "paper_id": req.paper_id
        }
        try:
            print(f"[DEBUG] 启动线程生成报告: task_id={task_id}")
            thread = threading.Thread(
                target=generate_report_task, 
                args=(task_id, user_id, req.paper_id, report_tasks, SessionLocal), 
                daemon=True
            )
            thread.start()
            print(f"[DEBUG] 线程已启动: {thread.name}, 是否活跃: {thread.is_alive()}")
        except Exception as e:
            print(f"[ERROR] 启动线程失败: {str(e)}")
            import traceback
            print(f"[ERROR] 详细错误: {traceback.format_exc()}")
            report_tasks[task_id]["status"] = "failed"
            report_tasks[task_id]["error_message"] = f"启动任务失败: {str(e)}"
        task_ids.append(task_id)
    print(f"[DEBUG] 返回任务ID: {task_ids}")
    return {"success": True, "task_ids": task_ids}

@router.get("/status")
async def get_report_status(task_ids: List[str] = Query(None, alias="task_ids[]")):
    result = {}
    if task_ids:
        for tid in task_ids:
            if tid in report_tasks:
                result[tid] = {
                    "status": report_tasks[tid]["status"],
                    "progress": report_tasks[tid]["progress"],
                    "file_path": report_tasks[tid]["file_path"],
                    "error_message": report_tasks[tid]["error_message"]
                }
            else:
                result[tid] = {"status": "not_found", "progress": 0}
    return result

@router.get("/download/{task_id}")
def download_report(task_id: str):
    task = report_tasks.get(task_id)
    if not task or task["status"] != "completed" or not task["file_path"]:
        raise HTTPException(status_code=404, detail="报告未生成或不存在")
    return FileResponse(task["file_path"], filename=os.path.basename(task["file_path"]))

@router.post("/batch/download")
def batch_download_reports(report_ids: List[int]):
    """批量下载报告，返回下载链接"""
    download_links = []
    for report_id in report_ids:
        download_links.append({
            "report_id": report_id,
            "download_url": f"/reports/{report_id}/download"
        })
    return {"success": True, "download_links": download_links} 