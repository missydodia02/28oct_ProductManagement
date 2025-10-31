# main.py
"""
FastAPI app for:
 - uploading CSV and saving to PostgreSQL using Prisma
 - adding product via JSON POST
 - exporting products to CSV or XLSX for download

Read comments below carefully — each important step is explained in easy English.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prisma import Prisma                       # Prisma client
import csv
import io
import os
from dotenv import load_dotenv
import pandas as pd                             # used for Excel export
from typing import List

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Product Management (CSV import/export)")

# Allow CORS (so you can call from browser or Postman easily)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # for development allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a Prisma client instance (async)
db = Prisma()

# Pydantic model for input validation when adding a product via JSON
class ProductIn(BaseModel):
    name: str
    price: float
    quantity: int
    category: str

# Start-up event: connect Prisma to DB when the app starts
@app.on_event("startup")
async def startup():
    # Connect Prisma client to the database
    await db.connect()

# Shutdown event: disconnect Prisma when the app stops
@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

# Route 1: Add single product via JSON (POST /add-product)
@app.post("/add-product", status_code=201)
async def add_product(payload: ProductIn):
    """
    Add a product using JSON body.
    Example JSON:
    {
      "name": "Laptop",
      "price": 45000,
      "quantity": 10,
      "category": "Electronics"
    }
    """
    # Use Prisma to create a new record in Product table
    created = await db.product.create(
        data={
            "name": payload.name,
            "price": payload.price,
            "quantity": payload.quantity,
            "category": payload.category,
        }
    )
    # Return the created record (Prisma model -> dict-like)
    return created

# Helper: parse CSV file bytes to list of dicts
def parse_csv_bytes(file_bytes: bytes) -> List[dict]:
    """
    Read CSV bytes and return a list of dictionaries.
    Assumes CSV header contains: name,price,quantity,category
    """
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for r in reader:
        # Convert fields to correct types and append
        try:
            row = {
                "name": r.get("name", "").strip(),
                "price": float(r.get("price", 0) or 0),
                "quantity": int(float(r.get("quantity", 0) or 0)),
                "category": r.get("category", "").strip(),
            }
            rows.append(row)
        except Exception as e:
            # Skip row or raise, here we raise to make the error visible
            raise ValueError(f"Invalid row in CSV: {r} -> {e}")
    return rows

# Route 2: Upload CSV and bulk insert (POST /upload-csv)
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file. The CSV must have header:
    name,price,quantity,category

    Each row will be inserted into the Product table.
    """
    # Check filename extension for basic validation
    filename = file.filename
    if not (filename.lower().endswith(".csv")):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    # Read file bytes (async)
    content = await file.read()

    # Parse CSV to list of dicts
    try:
        rows = parse_csv_bytes(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Insert rows one by one (we could use transaction or bulk if needed)
    created = []
    for r in rows:
        rec = await db.product.create(data=r)
        created.append(rec)

    return {"inserted": len(created), "details": created}

# Route 3: Download all products as CSV (GET /download-csv)
@app.get("/download-csv")
async def download_csv():
    """
    Fetch all products and return a CSV file for download.
    """
    # Fetch all products from DB
    products = await db.product.find_many()

    # Create CSV in-memory
    output = io.StringIO()
    fieldnames = ["id", "name", "price", "quantity", "category"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for p in products:
        writer.writerow({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "quantity": p.quantity,
            "category": p.category
        })

    # Save to a temporary file (so FastAPI can return a FileResponse)
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    file_path = os.path.join(exports_dir, "products_export.csv")
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(output.getvalue())

    return FileResponse(path=file_path, filename="products_export.csv", media_type="text/csv")

# Route 4: Download all products as XLSX (GET /download-xlsx)
@app.get("/download-xlsx")
async def download_xlsx():
    """
    Fetch all products and return an XLSX file for download.
    We use pandas to create the Excel file easily.
    """
    products = await db.product.find_many()

    # Convert Prisma model list to list of dicts for pandas
    rows = []
    for p in products:
        rows.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "quantity": p.quantity,
            "category": p.category
        })

    # Create DataFrame and write to XLSX file
    df = pd.DataFrame(rows)
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    file_path = os.path.join(exports_dir, "products_export.xlsx")
    df.to_excel(file_path, index=False)

    return FileResponse(path=file_path, filename="products_export.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
