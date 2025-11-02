# model.py
# This file defines the Pydantic models for input validation.

from pydantic import BaseModel

class ProductIn(BaseModel):
    name: str
    price: float
    quantity: int
    category: str
