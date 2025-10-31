# app/routes/product_routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.config.database import get_db
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductResponse

from app.models.category_model import Category
from app.models.company_model import Company

router = APIRouter(prefix="/products", tags=["Products"])

# Create product
@router.post("/", response_model=ProductResponse)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    # Check duplicate by name + company (prevent same product twice for same company)
    existing = db.query(Product).filter(
        Product.name == payload.name,
        Product.company_id == payload.company_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists for this company")

    product = Product(**payload.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# # Read all (with pagination)
# @router.get("/", response_model=List[ProductResponse])
# def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     return db.query(Product).offset(skip).limit(limit).all()
# Read all (with pagination + include category/company names)
@router.get("/", response_model=List[ProductResponse])
def list_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .join(Category, Product.category_id == Category.id)
        .join(Company, Product.company_id == Company.id)
        .add_columns(Product.id, Product.name, Product.price, Category.name.label("category_name"), Company.name.label("company_name"))
        .offset(skip)
        .limit(limit)
        .all()
    )
    # convert result into readable list
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "category_name": p.category_name,
            "company_name": p.company_name
        }
        for p in products
    ]


# # Get single product by id
# @router.get("/{product_id}", response_model=ProductResponse)
# def get_product(product_id: int, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product
# Get single product by id (include category/company names)
@router.get("/{product_id}", response_model=dict)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .join(Category, Product.category_id == Category.id)
        .join(Company, Product.company_id == Company.id)
        .add_columns(Product.id, Product.name, Product.price, Category.name.label("category_name"), Company.name.label("company_name"))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "category_name": product.category_name,
        "company_name": product.company_name
    }



# Update product
@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.dict().items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product

# Delete product
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}

# Search API: q searches name and description, filter by company_id and category_id, pagination
@router.get("/search", response_model=List[ProductResponse])
def search_products(
    q: Optional[str] = Query(None, description="Search term for name or description"),
    company_id: Optional[int] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if q:
        like_q = f"%{q}%"
        query = query.filter((Product.name.ilike(like_q)) | (Product.description.ilike(like_q)))
    if company_id:
        query = query.filter(Product.company_id == company_id)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    results = query.offset(skip).limit(limit).all()
    if not results:
        # return empty list instead of 404 for search (more user-friendly)
        return []
    return results
