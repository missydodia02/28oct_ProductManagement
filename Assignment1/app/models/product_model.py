# app/models/product_model.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

# Product table: stores product details with foreign keys to company and category
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)      # primary key
    name = Column(String, nullable=False, index=True)       # product name
    description = Column(String, nullable=True)             # optional description
    price = Column(Float, nullable=False)                   # product price
    stock = Column(Integer, nullable=False, default=0)      # stock quantity

    # Foreign keys pointing to Company and Category
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Relationships to access Company and Category objects from Product
    company = relationship("Company", back_populates="products")
    category = relationship("Category", back_populates="products")
