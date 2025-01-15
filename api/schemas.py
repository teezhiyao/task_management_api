from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class RoleBase(BaseModel):
    role_name: str

class RoleCreate(RoleBase):
    pass  

class RoleResponse(RoleBase):
    role_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    role_id: int  # Should match a valid role, e.g., "Employer" or "Employee"

class UserLogin(UserBase):
    hashed_password: str  

class UserResponse(UserBase):
    user_id: int
    role_id: int  # Should match a valid role, e.g., "Employer" or "Employee"
    created_at: Optional[str]  # Optional field for response

    class Config:
        orm_mode = True

        
class TaskBase(BaseModel):
    task_description: Optional[str] = None
    status: Optional[str] = None # Expected values: "Pending", "In Progress", "Completed"
    due_date: Optional[datetime] = datetime.now()  # Format: YYYY-MM-DD
    creation_date: Optional[datetime] = datetime.now()
    assignee_id: Optional[int] = None

class TaskCreate(TaskBase):
    task_name: str

class TaskResponse(TaskBase):
    task_id: int

    class Config:
        orm_mode = True

class EmployeeTaskSummary(BaseModel):
    user_id: int
    username: str
    total_tasks: int
    completed_tasks: int

    class Config:
        orm_mode = True

# https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#global-view 
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    scopes: list[str] = []