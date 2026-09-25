from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Task, User
from schemas import TaskCreate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[TaskOut])
def list_tasks(
    completed: bool | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Task).filter(Task.owner_id == user.id)
    if completed is not None:
        q = q.filter(Task.completed == completed)
    # TODO: paginate once task lists get big
    return q.order_by(Task.due_date.is_(None), Task.due_date).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not payload.title.strip():
        raise HTTPException(400, "Title cannot be empty")

    task = Task(**payload.model_dump(), owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    payload: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(404, "Task {} not found".format(task_id))

    if not payload.title.strip():
        raise HTTPException(400, "Title cannot be empty")

    # full replace, PUT semantics - omitted fields fall back to schema defaults
    task.title = payload.title
    task.description = payload.description
    task.due_date = payload.due_date
    task.completed = payload.completed

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(404, "Task {} not found".format(task_id))

    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
