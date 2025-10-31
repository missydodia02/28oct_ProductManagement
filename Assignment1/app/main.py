# app/main.py

from fastapi import FastAPI
from app.config.database import Base, engine
from app.routes import product_routes, company_routes, category_routes

# Create all tables in DB (if they do not exist). This uses SQLAlchemy metadata.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Management API - Assignment 1")

# Include routers for modular endpoints
app.include_router(company_routes.router)
app.include_router(category_routes.router)
app.include_router(product_routes.router)

@app.get("/")
def root():
    return {"message": "Product Management API is running. Visit /docs for Swagger UI."}
