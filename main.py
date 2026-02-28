import os
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
import bcrypt
from pydantic import BaseModel
import re
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDBModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="CRUD Teste", version="1.0.0")

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    id: int
    name: str
    email: str
    created_at: str
    updated_at: str

def validateEmail(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# CREATE
@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(UserDBModel).filter(UserDBModel.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not validateEmail(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_db = UserDBModel(
        name=user.name.title(),
        email=user.email,
        password_hash=hashed,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db

# READ
@app.get("/users/{user_id}", response_model=User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/email/{user_email}", response_model=User)
def get_user_by_email(user_email: str, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.email == user_email).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# UPDATE
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed = bcrypt.hashpw(updated_user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.name=updated_user.name.title()
    user.email=updated_user.email
    user.password_hash=hashed
    user.updated_at=datetime.now().isoformat()
    
    db.commit()
    db.refresh(user)
    return user

# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db : Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}