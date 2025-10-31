# app/routes/company_routes.py

"""
Company Routes
---------------
In Java: similar to a Controller class that handles Company-related requests.
Uses Prisma ORM for database operations.
"""

from fastapi import APIRouter, HTTPException
from prisma import Prisma
from app.schemas.company_schema import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["Companies"])
prisma = Prisma()

# Create a new company
@router.post("/", response_model=CompanyResponse)
async def create_company(company: CompanyCreate):
    await prisma.connect()
    existing = await prisma.company.find_first(where={"name": company.name})
    if existing:
        await prisma.disconnect()
        raise HTTPException(status_code=400, detail="Company already exists.")
    new_company = await prisma.company.create(data=company.dict())
    await prisma.disconnect()
    return new_company

# Get all companies
@router.get("/", response_model=list[CompanyResponse])
async def get_companies():
    await prisma.connect()
    companies = await prisma.company.find_many()
    await prisma.disconnect()
    return companies

# Get company by ID
@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int):
    await prisma.connect()
    company = await prisma.company.find_unique(where={"id": company_id})
    await prisma.disconnect()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

# Delete a company
@router.delete("/{company_id}")
async def delete_company(company_id: int):
    await prisma.connect()
    company = await prisma.company.find_unique(where={"id": company_id})
    if not company:
        await prisma.disconnect()
        raise HTTPException(status_code=404, detail="Company not found")
    await prisma.company.delete(where={"id": company_id})
    await prisma.disconnect()
    return {"message": "Company deleted successfully"}



























# # app/routes/company_routes.py

# from fastapi import APIRouter, Depends, HTTPException
# from typing import List
# from sqlalchemy.orm import Session

# from app.config.database import get_db
# from app.models.company_model import Company
# from app.schemas.company_schema import CompanyCreate, CompanyResponse

# router = APIRouter(prefix="/companies", tags=["Companies"])

# @router.post("/", response_model=CompanyResponse)
# def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
#     existing = db.query(Company).filter(Company.name == payload.name).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Company already exists")
#     company = Company(**payload.dict())
#     db.add(company)
#     db.commit()
#     db.refresh(company)
#     return company

# @router.get("/", response_model=List[CompanyResponse])
# def list_companies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return db.query(Company).offset(skip).limit(limit).all()

# @router.get("/{company_id}", response_model=CompanyResponse)
# def get_company(company_id: int, db: Session = Depends(get_db)):
#     comp = db.query(Company).filter(Company.id == company_id).first()
#     if not comp:
#         raise HTTPException(status_code=404, detail="Company not found")
#     return comp
