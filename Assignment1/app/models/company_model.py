# app/models/company_model.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

# Company table: stores companies
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)  # primary key
    name = Column(String, unique=True, nullable=False)  # company name (unique)
    location = Column(String, nullable=True)            # optional location

    # Relationship: one company -> many products (back_populates links with Product.company)
    products = relationship("Product", back_populates="company", cascade="all, delete")
