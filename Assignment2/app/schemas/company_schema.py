# app/schemas/company_schema.py

from pydantic import BaseModel

# Shared properties for Company
class CompanyBase(BaseModel):
    name: str
    location: str | None = None

# Properties for creating a Company
class CompanyCreate(CompanyBase):
    pass

# Properties returned in responses
class CompanyResponse(CompanyBase):
    id: int

    class Config:
        orm_mode = True   # Allow ORM objects (SQLAlchemy) to be returned directly
