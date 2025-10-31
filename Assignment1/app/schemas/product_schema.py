# app/schemas/product_schema.py

from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)   # price must be >= 0
    stock: int = Field(..., ge=0)     # stock must be >= 0
    company_id: int
    category_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        orm_mode = True
