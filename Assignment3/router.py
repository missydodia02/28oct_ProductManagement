# router.py
# This file defines all API routes and uses service functions.

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from model import ProductIn
from service import add_product_service, bulk_insert_service, fetch_all_products, parse_csv_bytes
import csv
import io
import os

router = APIRouter()

# 1️⃣ Add product manually via JSON
@router.post("/add-product", status_code=201)
async def add_product(payload: ProductIn):
    created = await add_product_service(payload.dict())
    return created


# 2️⃣ Upload CSV and bulk insert
@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    content = await file.read()
    try:
        rows = parse_csv_bytes(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    created = await bulk_insert_service(rows)
    return {"inserted": len(created), "details": created}


# 3️⃣ Download all products as CSV
@router.get("/download-csv")
async def download_csv():
    products = await fetch_all_products()
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

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    file_path = os.path.join(exports_dir, "products_export.csv")
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(output.getvalue())

    return FileResponse(path=file_path, filename="products_export.csv", media_type="text/csv")
