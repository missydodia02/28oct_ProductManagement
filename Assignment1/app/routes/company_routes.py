# app/routes/company_routes.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.company_model import Company
from app.schemas.company_schema import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", response_model=CompanyResponse)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    company = Company(**payload.dict())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/", response_model=List[CompanyResponse])
def list_companies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Company).offset(skip).limit(limit).all()

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    comp = db.query(Company).filter(Company.id == company_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found")
    return comp
