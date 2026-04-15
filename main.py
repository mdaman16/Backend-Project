from fastapi import FastAPI, HTTPException
import asyncpg
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# -------------------- DB CONNECTION --------------------

class ProductCreate(BaseModel):
    productName: str
    productType: str
    unit: str
    supplierName: str
    costPrice: float
    sellingPrice: float
    taxCategory: str
    currentStock: float
    reorderLevel: float

class ProductResponse(BaseModel):
    productId: str
    productName: str
    productType: str
    unit: str
    supplierName: str
    costPrice: float
    sellingPrice: float
    taxCategory: str
    currentStock: float
    reorderLevel: float
    marginValue: float
    marginPercent: float
    inventoryValue: float
    stockStatus: str

class ProductListResponse(BaseModel):
    success: bool
    message: str
    data: List[ProductResponse]


class ProductCreateResponse(BaseModel):
    success: bool
    message: str
    data: ProductResponse

DB_CONFIG = {
    "user": "postgres",
    "password": "root",
    "database": "Demo",
    "host": "localhost",
    "port": 5432
}

pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(**DB_CONFIG)

@app.on_event("shutdown")
async def shutdown():
    await pool.close()

# -------------------- COMMON QUERY FUNCTION --------------------

async def execute_query(query: str, *args, fetch: bool = False):
    async with pool.acquire() as conn:
        if fetch:
            return await conn.fetch(query, *args)
        else:
            return await conn.execute(query, *args)

# -------------------- RAW MATERIAL APIs --------------------

@app.post("/raw-materials")
async def create_raw_material(name: str, unit: str, cost_per_unit: float):
    query = """
    INSERT INTO raw_materials (name, unit, cost_per_unit)
    VALUES ($1, $2, $3)
    RETURNING *
    """
    result = await execute_query(query, name, unit, cost_per_unit, fetch=True)
    return dict(result[0])

@app.get("/raw-materials")
async def get_raw_materials():
    query = "SELECT * FROM raw_materials"
    result = await execute_query(query, fetch=True)
    return [dict(r) for r in result]

# -------------------- INVENTORY APIs --------------------

@app.post("/inventory")
async def add_inventory(raw_material: str, lot_number: str, expiry_date: str, quantity: float):
    query = """
    INSERT INTO inventory (raw_material, lot_number, expiry_date, quantity)
    VALUES ($1, $2, $3, $4)
    RETURNING *
    """
    result = await execute_query(query, raw_material, lot_number, expiry_date, quantity, fetch=True)
    return dict(result[0])

@app.get("/inventory")
async def get_inventory():
    query = "SELECT * FROM inventory"
    result = await execute_query(query, fetch=True)
    return [dict(r) for r in result]



# -------------------- SALES APIs --------------------

@app.post("/sales")
async def create_sale(customer_name: str, quantity: float, price: float, discount: float):
    subtotal = quantity * price
    final_total = subtotal - discount

    query = """
    INSERT INTO sales_orders (customer_name, quantity, price, discount, final_total)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING *
    """
    result = await execute_query(query, customer_name, quantity, price, discount, final_total, fetch=True)
    return dict(result[0])

@app.get("/sales")
async def get_sales():
    query = "SELECT * FROM sales_orders"
    result = await execute_query(query, fetch=True)
    return [dict(r) for r in result]

# -------------------- DASHBOARD --------------------

@app.get("/dashboard")
async def dashboard():
    query = "SELECT COALESCE(SUM(final_total),0) as total_sales, COUNT(*) as total_orders FROM sales_orders"
    result = await execute_query(query, fetch=True)
    return dict(result[0])


from fastapi import HTTPException
import uuid

# -------------------- HELPER --------------------

def generate_product_id():
    return f"PRD-{str(uuid.uuid4().int)[:3]}"


def calculate_fields(cost_price, selling_price, current_stock, reorder_level):
    margin_value = selling_price - cost_price
    margin_percent = (margin_value / selling_price) * 100 if selling_price else 0
    inventory_value = current_stock * cost_price

    if current_stock <= reorder_level:
        stock_status = "Low"
    elif current_stock > reorder_level * 2:
        stock_status = "High"
    else:
        stock_status = "Medium"

    return margin_value, margin_percent, inventory_value, stock_status


# -------------------- CREATE PRODUCT --------------------

@app.post("/api/v1/products", response_model=ProductCreateResponse)
async def create_product(payload: ProductCreate):

    product_id = generate_product_id()

    query = """
    INSERT INTO products (
        product_id, product_name, product_type, unit,
        supplier_name, cost_price, selling_price,
        tax_category, current_stock, reorder_level
    )
    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
    RETURNING *
    """

    result = await execute_query(
        query,
        product_id,
        payload.productName,
        payload.productType,
        payload.unit,
        payload.supplierName,
        payload.costPrice,
        payload.sellingPrice,
        payload.taxCategory,
        payload.currentStock,
        payload.reorderLevel,
        fetch=True
    )

    if not result:
        raise HTTPException(status_code=500, detail="Insert failed")

    product = dict(result[0])

    margin_value, margin_percent, inventory_value, stock_status = calculate_fields(
        product["cost_price"],
        product["selling_price"],
        product["current_stock"],
        product["reorder_level"]
    )

    return {
        "success": True,
        "message": "Product created successfully.",
        "data": {
            "productId": product["product_id"],
            "productName": product["product_name"],
            "productType": product["product_type"],
            "unit": product["unit"],
            "supplierName": product["supplier_name"],
            "costPrice": float(product["cost_price"]),
            "sellingPrice": float(product["selling_price"]),
            "taxCategory": product["tax_category"],
            "currentStock": float(product["current_stock"]),
            "reorderLevel": float(product["reorder_level"]),
            "marginValue": round(margin_value, 2),
            "marginPercent": round(margin_percent, 2),
            "inventoryValue": round(inventory_value, 2),
            "stockStatus": stock_status
        }
    }


# -------------------- GET PRODUCTS --------------------

@app.get("/api/v1/products", response_model=ProductListResponse)
async def get_products():

    query = "SELECT * FROM products ORDER BY created_at DESC"
    result = await execute_query(query, fetch=True)

    data = []

    for r in result:
        product = dict(r)

        margin_value, margin_percent, inventory_value, stock_status = calculate_fields(
            product["cost_price"],
            product["selling_price"],
            product["current_stock"],
            product["reorder_level"]
        )

        data.append({
            "productId": product["product_id"],
            "productName": product["product_name"],
            "productType": product["product_type"],
            "unit": product["unit"],
            "supplierName": product["supplier_name"],
            "costPrice": float(product["cost_price"]),
            "sellingPrice": float(product["selling_price"]),
            "taxCategory": product["tax_category"],
            "currentStock": float(product["current_stock"]),
            "reorderLevel": float(product["reorder_level"]),
            "marginValue": round(margin_value, 2),
            "marginPercent": round(margin_percent, 2),
            "inventoryValue": round(inventory_value, 2),
            "stockStatus": stock_status
        })

    return {
        "success": True,
        "message": "Products fetched successfully.",
        "data": data
    }