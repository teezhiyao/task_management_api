from fastapi import Depends, FastAPI, HTTPException, Security, status
from . import models, schemas, crud
from .crud import SECRET_KEY, ALGORITHM
from .database import SessionLocal, engine
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from pydantic import BaseModel, ValidationError


ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="user/login",
    scopes={"employee": "Read information about the current user.", "employer": "Read items."},
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this if your frontend runs on a different port
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Role-based access control dependency
# def role_required(allowed_roles: List[str]):
#     def check_role(current_user: schemas.UserResponse = Depends(crud.get_user_by_id)):
#         if current_user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=403,
#                 detail="You do not have permission to perform this action."
#             )
#         return current_user
#     return check_role


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    print("hello get current")

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        print("sec scope", authenticate_value)
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        print("Token:", token)
        print("Payload:", payload)
        print("Scopes:", security_scopes.scopes)
        print("User:", username)
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenData(scopes=token_scopes, username=username)
        print(token_data)

    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    # user = get_user(fake_users_db, username=token_data.username)
    user = crud.get_user_by_username(token_data.username, db)

    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.UserBase, Security(get_current_user)],
):


    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Create new user
@app.post("/user", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(user, db)

@app.post("/user/login")
async def login_for_access_token(user: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> schemas.Token:
    user_db_info = crud.get_user_by_username(user.username, db)
    if not user_db_info:
        raise HTTPException(status_code=400, detail="User not found")
    if not pwd_context.verify(user.password, user_db_info.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")


    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    print('user username', user.username)
    print(user_db_info.role_id)
    role_mapping = {1:"employer", 2:"employee"}
    print('scope', [role_mapping[user_db_info.role_id]])

    access_token = create_access_token(
        data={"sub": user.username, "scopes": [role_mapping[user_db_info.role_id]]},
        # data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return schemas.Token(access_token=access_token, token_type="bearer")

# Create new task
@app.post("/task", response_model=schemas.TaskBase)
async def create_task(
    task: schemas.TaskBase,
    current_user: Annotated[schemas.UserResponse, Security(get_current_active_user, scopes=["employer"])],
    db: Session = Depends(get_db)
):
    return crud.create_task(task, db)
#
# # View all tasks (with filter and sort)
# @app.get("/task", response_model=list[schemas.TaskBase])
# def get_tasks(
#     status: str = None,
#     sort_by: str = "creation_date",
#     db: Session = Depends(get_db),
#     current_user: schemas.UserResponse = Depends(role_required(["Employee", "Employer"]))  # Allow both roles
# ):
#     if current_user.role == "Employee":
#         return crud.get_tasks(assignee_id=current_user.id, status=status, sort_by=sort_by, db=db)
#     return crud.get_tasks(status=status, sort_by=sort_by, db=db)
#
# # # Employee Task Summary
# # @app.get("/task/all", response_model=list[schemas.EmployeeTaskSummary])
# # def get_employee_task_summary(
# #     db: Session = Depends(get_db),
# #     current_user: schemas.UserResponse = Depends(role_required(["Employer"]))
# # ):
# #     return crud.get_employee_task_summary(db)
#
# # Update a task
# @app.put("/task", response_model=schemas.TaskBase)
# def update_task(task_id: int, task_update: schemas.TaskBase, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(role_required(["Employee", "Employer"]))):
#     return crud.update_task(task_id, task_update, db)
#
# # Assign a task
# @app.put("/task/{user_id}", response_model=schemas.TaskBase)
# def assign_task(
#     user_id: int,
#     task_id: int,
#     db: Session = Depends(get_db),
#     current_user: schemas.UserResponse = Depends(role_required(["Employer"]))
# ):
#     return crud.assign_task(user_id, task_id, db)
#
# # Get tasks of a user
# @app.get("/user/task", response_model=list[schemas.TaskBase])
# def get_user_tasks(db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(crud.get_current_user)):
#     return crud.get_user_tasks(current_user.id, db)

