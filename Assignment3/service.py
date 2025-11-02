# service.py
# This file contains helper functions that interact with the database.

from prisma import Prisma
import csv
import io
from fastapi import HTTPException
from typing import List

# Create Prisma client
db = Prisma()

async def connect_db():
    """Connect Prisma to database"""
    await db.connect()

async def disconnect_db():
    """Disconnect Prisma from database"""
    await db.disconnect()


# ---------------- CSV Parsing ---------------- #
def parse_csv_bytes(file_bytes: bytes) -> List[dict]:
    """Convert CSV file bytes into a list of dictionaries"""
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for r in reader:
        try:
            row = {
                "name": r.get("name", "").strip(),
                "price": float(r.get("price", 0) or 0),
                "quantity": int(float(r.get("quantity", 0) or 0)),
                "category": r.get("category", "").strip(),
            }
            rows.append(row)
        except Exception as e:
            raise ValueError(f"Invalid row in CSV: {r} -> {e}")
    return rows


# ---------------- Product Services ---------------- #
async def add_product_service(data):
    """Insert one product into DB"""
    return await db.product.create(data=data)

async def bulk_insert_service(rows):
    """Insert multiple products (from CSV)"""
    created = []
    for r in rows:
        rec = await db.product.create(data=r)
        created.append(rec)
    return created

async def fetch_all_products():
    """Fetch all products from DB"""
    return await db.product.find_many()
