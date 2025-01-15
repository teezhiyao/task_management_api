from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException
from sqlalchemy.sql import case, func
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

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

def get_tasks(assignee_id: int = None, status: str = None, sort_by: str = None, status_order: str = None, db: Session = None):
    query = db.query(models.Task)
    print("assignee_id ", assignee_id)
    print("status ", status)
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    if status:
        query = query.filter(models.Task.status == status)
    if sort_by == "creation_date":
        query = query.order_by(models.Task.creation_date)
    elif sort_by == "due_date":
        query = query.order_by(models.Task.due_date)

    if status_order:
        case_statement = case(
            (models.Task.status == status_order, 0),  # Rank `prioritize_status` as 0
            else_=1  # Rank all other statuses as 1
        )
        query = query.order_by(case_statement)

    return query.all()

def update_task(update_data: dict, task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not task:
        return None

    # Update the task with the provided data
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task



# Summary Operations
def get_employee_task_summary(db: Session):
    completed_tasks_case = case(
        (models.Task.status == "completed", 1), else_=0
    )

    query = (
        db.query(
            models.User.user_id,
            models.User.username,
            func.count(models.Task.task_id).label("total_tasks"),
            func.sum(completed_tasks_case).label("completed_tasks"),
        )
        .join(models.Task, models.User.user_id == models.Task.assignee_id, isouter=True)
        .group_by(models.User.user_id)
        .order_by(models.User.user_id)
    )
    return query.all()