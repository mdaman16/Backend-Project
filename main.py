from fastapi import FastAPI, HTTPException
import asyncpg

app = FastAPI()

# -------------------- DB CONNECTION --------------------

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

# -------------------- PRODUCT APIs --------------------

@app.post("/products")
async def create_product(name: str, batch_size: float):
    query = """
    INSERT INTO products (name, batch_size)
    VALUES ($1, $2)
    RETURNING *
    """
    result = await execute_query(query, name, batch_size, fetch=True)
    return dict(result[0])

@app.get("/products")
async def get_products():
    query = "SELECT * FROM products"
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
