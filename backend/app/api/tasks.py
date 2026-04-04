from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models import Task, User
from app.api.auth import get_current_user
from app.agents.trend import TrendAgent
from app.agents.writer import WriterAgent

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskCreate(BaseModel):
    task_type: str
    input_data: Dict[str, Any]

class TaskResponse(BaseModel):
    id: int
    task_type: str
    status: str
    input_data: Optional[Dict[str, Any]]
    result_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = Task(
        user_id=current_user.id,
        task_type=task.task_type,
        status="pending",
        input_data=task.input_data
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 异步处理任务
    try:
        if task.task_type == "trend_analysis":
            agent = TrendAgent()
            result = await agent.analyze(task.input_data)
            db_task.result_data = result
            db_task.status = "completed"
        elif task.task_type == "write_chapter":
            agent = WriterAgent()
            result = await agent.write(task.input_data)
            db_task.result_data = result
            db_task.status = "completed"
        else:
            db_task.status = "failed"
            db_task.result_data = {"error": "Unknown task type"}
    except Exception as e:
        db_task.status = "failed"
        db_task.result_data = {"error": str(e)}

    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
