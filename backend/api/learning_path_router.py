from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from database.connect import get_db
from api.common import get_current_user
from database.crud_learning_path import save_learning_path, get_learning_path, get_user_learning_paths, delete_learning_path
from utils.response import success

router = APIRouter(prefix="/learning-path", tags=["学习路径模块"])


class LearningPathStep(BaseModel):
    id: int
    title: str
    description: str
    status: str = "pending"
    date: str = ""
    duration: int = 45


class SaveLearningPathRequest(BaseModel):
    goal: str
    steps: List[Dict[str, Any]]


class LearningPathResponse(BaseModel):
    id: int
    user_id: int
    goal: str
    steps: List[Dict[str, Any]]
    created_at: str
    updated_at: str


@router.get("/list")
def list_learning_paths(
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    paths = get_user_learning_paths(db=db, user_id=current_login_uid)
    result = []
    for p in paths:
        result.append({
            "id": p.id,
            "user_id": p.user_id,
            "goal": p.goal,
            "steps": p.steps,
            "created_at": str(p.created_at) if p.created_at else "",
            "updated_at": str(p.updated_at) if p.updated_at else "",
        })
    return success(data={"paths": result})


@router.get("/{goal}")
def get_one_learning_path(
    goal: str,
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    path = get_learning_path(db=db, user_id=current_login_uid, goal=goal)
    if not path:
        return success(data={"path": None, "steps": []})
    return success(data={
        "path": {
            "id": path.id,
            "user_id": path.user_id,
            "goal": path.goal,
            "steps": path.steps,
            "created_at": str(path.created_at) if path.created_at else "",
            "updated_at": str(path.updated_at) if path.updated_at else "",
        },
        "steps": path.steps
    })


@router.post("/save")
def save_learning_path_api(
    req: SaveLearningPathRequest,
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    saved = save_learning_path(
        db=db,
        user_id=current_login_uid,
        goal=req.goal,
        steps=req.steps
    )
    return success(data={
        "id": saved.id,
        "goal": saved.goal,
        "steps": saved.steps,
        "updated_at": str(saved.updated_at) if saved.updated_at else "",
    })


@router.delete("/{goal}")
def delete_learning_path_api(
    goal: str,
    db: Session = Depends(get_db),
    current_login_uid: int = Depends(get_current_user)
):
    delete_learning_path(db=db, user_id=current_login_uid, goal=goal)
    return success(data={"msg": f"学习路径「{goal}」已删除"})