from fastapi import FastAPI, HTTPException
import bcrypt
from pydantic import BaseModel
import re
from typing import List, Optional

app = FastAPI(title="CRUD Teste", version="1.0.0")

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    id: int
    name: str
    email: str

class UserDB(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str

banco: List[UserDB] = []

# CREATE
@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    for existing_user in banco:
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    validMail = validateEmail(user.email)
    if not validMail:
        raise HTTPException(status_code=400, detail="Invalid email format")
    if len(user.password) < 7:
        raise HTTPException(status_code=400, detail="Password must be at least 7 characters long")
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_db = UserDB(
        id=len(banco) + 1,
        name=user.name.title(),
        email=user.email,
        password_hash=hashed
    )
    banco.append(user_db)
    return user_db

# READ
@app.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: int):
    for user in banco:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/email/{user_email}", response_model=User)
def get_user_by_email(user_email: str):
    for user in banco:
        if user.email == user_email:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# UPDATE
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: UserCreate):
    for index, user in enumerate(banco):
        if user.id == user_id:
            hashed = bcrypt.hashpw(updated_user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            newUser = UserDB(
                id=user_id,
                name=updated_user.name,
                email=updated_user.email,
                password_hash=hashed
            )
            banco[index] = newUser
            return newUser
    raise HTTPException(status_code=404, detail="User not found")

# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(banco):
        if user.id == user_id:
            banco.pop(index)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


def validateEmail(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None