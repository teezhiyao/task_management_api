# models.py
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text, TIMESTAMP, func, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class TaskStatus(str, enum.Enum):
    pending = "Pending"
    in_progress = "In Progress"
    completed = "Completed"

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)

    # Relationship to User
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)
    # created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="users")
    assigned_tasks = relationship("Task", foreign_keys="[Task.assignee_id]", back_populates="assignee")

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(200), nullable=False)
    task_description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Relationships
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")