from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field

import crud

app = FastAPI(title="Users & Posts")


# --- схеми -------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    post_titles: list[str] = []


class UserEmailUpdate(BaseModel):
    email: EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: Optional[str]
    user_id: int


# --- маршрути ----------------------------------------------------------------

@app.get("/")
def index():
    return {"service": "users-posts", "docs": "/docs"}


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(data: UserCreate):
    user = crud.create_user_with_posts(data.username, data.email, data.post_titles)
    if user is None:
        raise HTTPException(status_code=409, detail="Username or email already exists")
    return user


@app.get("/users", response_model=list[UserOut])
def get_users():
    return crud.get_all_users()


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = crud.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserOut)
def update_user_email(user_id: int, data: UserEmailUpdate):
    user = crud.update_user_email(user_id, data.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if not crud.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/posts", response_model=list[PostOut])
def get_posts():
    return crud.get_all_posts()
