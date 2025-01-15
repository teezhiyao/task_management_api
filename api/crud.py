from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD Operations
def create_user(user: schemas.UserCreate, db: Session):
    # Check if role_id exists
    role = db.query(models.Role).filter(models.Role.role_id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Invalid role_id")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password

    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(user_id: int, db: Session):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(username: str, db: Session):
    return db.query(models.User).filter(models.User.username == username).first()

def get_all_users(db: Session):
    return db.query(models.User).all()


# Task CRUD Operations
def create_task(task: schemas.TaskBase, db: Session):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task_by_id(task_id: int, db: Session):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(assignee_id: int = None, status: str = None, sort_by: str = None, db: Session = None):
    query = db.query(models.Task)
    
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    if status:
        query = query.filter(models.Task.status == status)
    if sort_by == "creation_date":
        query = query.order_by(models.Task.creation_date)
    elif sort_by == "due_date":
        query = query.order_by(models.Task.due_date)
    
    return query.all()

def assign_task(user_id: int, task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
    task.assignee_id = user_id
    db.commit()
    db.refresh(task)
    return task

def update_task_status(task_id: int, status: str, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return None
    task.status = status
    db.commit()
    db.refresh(task)
    return task


# Summary Operations
def get_employee_task_summary(db: Session):
    users = db.query(models.User).filter(models.User.role == "Employee").all()
    summary = []
    for user in users:
        total_tasks = db.query(models.Task).filter(models.Task.assignee_id == user.id).count()
        completed_tasks = db.query(models.Task).filter(
            models.Task.assignee_id == user.id, models.Task.status == "Completed"
        ).count()
        summary.append({
            "user_id": user.id,
            "name": user.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks
        })
    return summary