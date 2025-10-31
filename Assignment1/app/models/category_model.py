# app/models/category_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

# Category table: stores product categories
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)  # primary key
    name = Column(String, unique=True, nullable=False)  # category name (unique)

    # One category can have many products one to many
    products = relationship("Product", back_populates="category", cascade="all, delete")
