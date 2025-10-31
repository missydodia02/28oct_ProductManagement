# app/routes/category_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.category_model import Category
from app.schemas.category_schema import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = Category(**payload.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/", response_model=List[CategoryResponse])
def list_categories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Category).offset(skip).limit(limit).all()
