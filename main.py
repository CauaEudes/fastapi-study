from fastapi import FastAPI, HTTPException
import bcrypt
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="CRUD Teste", version="1.0.0")

class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

banco = []

# CREATE
@app.post("/users", response_model=User)
def create_user(user: User):
    banco.append(user)
    return user

# READ
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in banco:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# UPDATE
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for index, user in enumerate(banco):
        if user.id == user_id:
            banco[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(banco):
        if user.id == user_id:
            banco.pop(index)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# LIST
@app.get("/users", response_model=List[User])
def list_users():
    return banco


