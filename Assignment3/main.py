# main.py
# Main entry point — starts FastAPI app and registers routes.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router
from service import connect_db, disconnect_db

app = FastAPI(title="Product Management (CSV Import/Export)")

# Allow Swagger + Postman access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect/Disconnect DB automatically
@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# Register router
app.include_router(router)

# Run using:  uvicorn main:app --reload













# # main.py
# """
# FastAPI Application for Product Management using Prisma ORM and PostgreSQL


# 1️Add product manually (via JSON request)
# 2️Upload products in bulk using CSV file
# 3️Export all products from database into a downloadable CSV file

# 👉 Uses Prisma for database operations
# 👉 Uses FastAPI for API routes
# 👉 Uses async/await for non-blocking DB access
# """

# # -------------------- IMPORT REQUIRED LIBRARIES --------------------
# from fastapi import FastAPI, UploadFile, File, HTTPException   # For building API and file upload
# from fastapi.responses import FileResponse                     # To send a file as response (for download)
# from fastapi.middleware.cors import CORSMiddleware              # Allow access from Swagger / browser / Postman
# from pydantic import BaseModel                                  # For input validation
# from prisma import Prisma                                       # Prisma client for database interaction
# from dotenv import load_dotenv                                  # To load .env file (contains DATABASE_URL)
# from typing import List                                         # For type hinting
# import csv                                                      # For reading/writing CSV files
# import io                                                       # For handling files in memory (no need to save temporarily)
# import os                                                       # For folder/file path creation

# # -------------------- LOAD ENVIRONMENT VARIABLES --------------------
# # Load the .env file so Prisma can read DATABASE_URL
# load_dotenv()

# # -------------------- CREATE FASTAPI APP --------------------
# app = FastAPI(title="Product Management (CSV Import/Export)")

# # -------------------- ENABLE CORS --------------------
# # CORS allows this API to be called from any frontend or Swagger UI
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],        # "*" means all origins allowed (localhost, swagger, postman, etc.)
#     allow_methods=["*"],        # Allow all HTTP methods (GET, POST, etc.)
#     allow_headers=["*"],        # Allow all headers (like Content-Type)
# )

# # -------------------- INITIALIZE PRISMA CLIENT --------------------
# # Prisma connects our FastAPI app with PostgreSQL
# db = Prisma()

# # -------------------- DEFINE PYDANTIC MODEL FOR VALIDATION --------------------
# # This model ensures that incoming JSON requests have correct fields and types
# class ProductIn(BaseModel):
#     name: str
#     price: float
#     quantity: int
#     category: str

# # -------------------- STARTUP EVENT --------------------
# @app.on_event("startup")
# async def startup():
#     """
#     This function automatically runs when FastAPI app starts.
#     It connects Prisma client to the database.
#     """
#     await db.connect()

# # -------------------- SHUTDOWN EVENT --------------------
# @app.on_event("shutdown")
# async def shutdown():
#     """
#     This function runs when FastAPI app stops.
#     It safely disconnects Prisma from the database.
#     """
#     await db.disconnect()

# # =====================================================================
# #                      ROUTE 1 → ADD SINGLE PRODUCT
# # =====================================================================
# @app.post("/add-product", status_code=201)
# async def add_product(payload: ProductIn):
    
#     # Create a new product record in PostgreSQL using Prisma
#     created = await db.product.create(
#         data={
#             "name": payload.name,
#             "price": payload.price,
#             "quantity": payload.quantity,
#             "category": payload.category,
#         }
#     )

#     # Return the inserted record as response
#     return created

# # =====================================================================
# #                      HELPER FUNCTION → PARSE CSV
# # =====================================================================
# def parse_csv_bytes(file_bytes: bytes) -> List[dict]:
#     """
#     Read CSV bytes and return a list of dictionaries.
#     Each row in the CSV file must contain:
#     name, price, quantity, category
#     """
#     # Decode binary CSV file into text (utf-8 encoding)
#     text = file_bytes.decode("utf-8")

#     # Use DictReader to automatically map CSV columns → dict keys
#     reader = csv.DictReader(io.StringIO(text))
#     rows = []

#     # Loop through each CSV row
#     for r in reader:
#         try:
#             # Clean and convert each field to correct type
#             row = {
#                 "name": r.get("name", "").strip(),
#                 "price": float(r.get("price", 0) or 0),
#                 "quantity": int(float(r.get("quantity", 0) or 0)),
#                 "category": r.get("category", "").strip(),
#             }
#             rows.append(row)
#         except Exception as e:
#             # If any row has wrong format or value, raise error
#             raise ValueError(f"Invalid row in CSV: {r} -> {e}")
#     return rows

# # =====================================================================
# #                      ROUTE 2 → UPLOAD CSV FILE
# # =====================================================================
# @app.post("/upload-csv")
# async def upload_csv(file: UploadFile = File(...)):
#     """
#     Upload a CSV file containing products.
#     CSV file must have header: name,price,quantity,category

#     Example CSV content:
#     name,price,quantity,category
#     Laptop,65000,5,Electronics
#     T-shirt,500,15,Fashion
#     """
#     # Step 1: Check file extension
#     filename = file.filename
#     if not filename.lower().endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Please upload a .csv file only.")

#     # Step 2: Read file content (async)
#     content = await file.read()

#     # Step 3: Convert CSV bytes → list of dictionaries
#     try:
#         rows = parse_csv_bytes(content)
#     except ValueError as e:
#         # Handle parsing error gracefully
#         raise HTTPException(status_code=400, detail=str(e))

#     # Step 4: Insert each product record into DB
#     created = []
#     for r in rows:
#         rec = await db.product.create(data=r)
#         created.append(rec)

#     # Step 5: Return success message and total inserted rows
#     return {"inserted": len(created), "details": created}

# # =====================================================================
# #                      ROUTE 3 → DOWNLOAD PRODUCTS AS CSV
# # =====================================================================
# @app.get("/download-csv")
# async def download_csv():
#     """
#     Fetch all products from database and return them as a downloadable CSV file.
#     """
#     # Step 1: Fetch all product records
#     products = await db.product.find_many()

#     # Step 2: Create CSV in-memory (no temporary file yet)
#     output = io.StringIO()
#     fieldnames = ["id", "name", "price", "quantity", "category"]

#     # DictWriter writes dicts → CSV rows easily
#     writer = csv.DictWriter(output, fieldnames=fieldnames)
#     writer.writeheader()  # write column headers first

#     # Step 3: Write all product rows
#     for p in products:
#         writer.writerow({
#             "id": p.id,
#             "name": p.name,
#             "price": p.price,
#             "quantity": p.quantity,
#             "category": p.category
#         })

#     # Step 4: Create folder "exports" if not already existing
#     exports_dir = "exports"
#     os.makedirs(exports_dir, exist_ok=True)

#     # Step 5: Save the generated CSV file
#     file_path = os.path.join(exports_dir, "products_export.csv")
#     with open(file_path, "w", encoding="utf-8", newline="") as f:
#         f.write(output.getvalue())

#     # Step 6: Return CSV file as downloadable response
#     return FileResponse(
#         path=file_path,
#         filename="products_export.csv",
#         media_type="text/csv"
#     )

# # =====================================================================
# # ✅ END OF FILE
# # =====================================================================

















