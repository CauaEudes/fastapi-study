from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import bcrypt
from datetime import datetime

from database import get_db
from models import UserDBModel
from schemas import UserCreate, User, validateEmail, validateCpf, cleanCpf

router = APIRouter(prefix="/users", tags=["Users"])

# CREATE
@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserDBModel).filter(UserDBModel.email == user.email).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not validateEmail(user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if not validateCpf(user.cpf):
        raise HTTPException(status_code=400, detail="Invalid CPF format")
    
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_db = UserDBModel(
        name=user.name.title(),
        email=user.email,
        cpf=cleanCpf(user.cpf),
        password_hash=hashed,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db

# READ
@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/email/{user_email}", response_model=User)
def get_user_by_email(user_email: str, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.email == user_email).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/cpf/{user_cpf}", response_model=User)
def get_user_by_cpf(user_cpf: str, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.cpf == cleanCpf(user_cpf)).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# UPDATE
@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    hashed = bcrypt.hashpw(updated_user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.name=updated_user.name.title()
    user.email=updated_user.email
    user.password_hash=hashed
    user.cpf=cleanCpf(updated_user.cpf)
    user.updated_at=datetime.now().isoformat()
    
    db.commit()
    db.refresh(user)
    return user

# DELETE
@router.delete("/{user_id}")
def delete_user(user_id: int, db : Session = Depends(get_db)):
    user = db.query(UserDBModel).filter(UserDBModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}