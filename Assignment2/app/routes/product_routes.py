# app/routes/product_routes.py

"""
Product Routes
---------------
In Java: similar to ProductController or Service layer using Hibernate Repository.
Includes CRUD + Search + Pagination.
"""

from fastapi import APIRouter, HTTPException, Query
from prisma import Prisma
from app.schemas.product_schema import ProductCreate, ProductResponse



router = APIRouter(prefix="/products", tags=["Products"])
prisma = Prisma()

# Create Product
@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    await prisma.connect()
    # check duplicate
    existing = await prisma.product.find_first(where={"name": product.name})
    if existing:
        await prisma.disconnect()
        raise HTTPException(status_code=400, detail="Product already exists.")
    new_product = await prisma.product.create(data=product.dict())
    await prisma.disconnect()
    return new_product

# Get all products with company and category names
@router.get("/", response_model=list[ProductResponse])
async def get_products(skip: int = 0, limit: int = 10):
    await prisma.connect()
    products = await prisma.product.find_many(
        skip=skip,
        take=limit,
        include={           # this will also fetch related company and category
            "company": True,
            "category": True
        }
    )
    await prisma.disconnect()
    return products


# Get single product by ID (with company and category names)
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    await prisma.connect()
    product = await prisma.product.find_unique(
        where={"id": product_id},
        include={           # also fetch company and category details
            "company": True,
            "category": True
        }
    )
    await prisma.disconnect()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Delete product
@router.delete("/{product_id}")
async def delete_product(product_id: int):
    await prisma.connect()
    product = await prisma.product.find_unique(where={"id": product_id})
    if not product:
        await prisma.disconnect()
        raise HTTPException(status_code=404, detail="Product not found")
    await prisma.product.delete(where={"id": product_id})
    await prisma.disconnect()
    return {"message": "Product deleted successfully"}

# Search products by name, category, price, or company
@router.get("/search/", response_model=list[ProductResponse])
async def search_products(
    q: str = Query("", description="Search keyword"),
    company_id: int | None = None,
    skip: int = 0,
    limit: int = 10
):
    await prisma.connect()
    where_clause = {
        "OR": [
            {"name": {"contains": q, "mode": "insensitive"}},
            {"description": {"contains": q, "mode": "insensitive"}}
        ]
    }
    if company_id:
        where_clause["company_id"] = company_id
    products = await prisma.product.find_many(where=where_clause, skip=skip, take=limit)
    await prisma.disconnect()
    return products

















# # app/routes/product_routes.py

# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from app.config.database import get_db
# from app.models.product_model import Product
# from app.schemas.product_schema import ProductCreate, ProductResponse

# router = APIRouter(prefix="/products", tags=["Products"])

# # Create product
# @router.post("/", response_model=ProductResponse)
# def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
#     # Check duplicate by name + company (prevent same product twice for same company)
#     existing = db.query(Product).filter(
#         Product.name == payload.name,
#         Product.company_id == payload.company_id
#     ).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Product already exists for this company")

#     product = Product(**payload.dict())
#     db.add(product)
#     db.commit()
#     db.refresh(product)
#     return product

# # Read all (with pagination)
# @router.get("/", response_model=List[ProductResponse])
# def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return db.query(Product).offset(skip).limit(limit).all()

# # Get single product by id
# @router.get("/{product_id}", response_model=ProductResponse)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

# # Update product
# @router.put("/{product_id}", response_model=ProductResponse)
# def update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     for key, value in payload.dict().items():
#         setattr(product, key, value)
#     db.commit()
#     db.refresh(product)
#     return product

# # Delete product
# @router.delete("/{product_id}")
# def delete_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     db.delete(product)
#     db.commit()
#     return {"detail": "Product deleted"}

# # Search API: q searches name and description, filter by company_id and category_id, pagination
# @router.get("/search", response_model=List[ProductResponse])
# def search_products(
#     q: Optional[str] = Query(None, description="Search term for name or description"),
#     company_id: Optional[int] = None,
#     category_id: Optional[int] = None,
#     skip: int = 0,
#     limit: int = 10,
#     db: Session = Depends(get_db),
# ):
#     query = db.query(Product)
#     if q:
#         like_q = f"%{q}%"
#         query = query.filter((Product.name.ilike(like_q)) | (Product.description.ilike(like_q)))
#     if company_id:
#         query = query.filter(Product.company_id == company_id)
#     if category_id:
#         query = query.filter(Product.category_id == category_id)
#     results = query.offset(skip).limit(limit).all()
#     if not results:
#         # return empty list instead of 404 for search (more user-friendly)
#         return []
#     return results
