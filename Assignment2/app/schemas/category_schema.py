# Pydantic model for Category
# -----------------------------------------------
# In Java: similar to a DTO class for transferring category data
from pydantic import BaseModel

# Base class (common fields)
class CategoryBase(BaseModel):
    name: str

# Schema used when creating a new category
class CategoryCreate(CategoryBase):
    pass

# Schema used in API responses
class CategoryResponse(CategoryBase):
    id: int

    class Config:
        orm_mode = True  # allows Prisma/ORM models to be converted to JSON


#same as the 1st assignment 