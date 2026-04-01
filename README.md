# FastAPI Inventory & Sales API (Async PostgreSQL)

## Overview

This project is a backend API built with FastAPI and PostgreSQL using async database access via `asyncpg`. It demonstrates a simple inventory and sales management system with direct SQL execution (no ORM).

The goal of this project is to provide a clean and minimal structure for learning how to build APIs with FastAPI while interacting with PostgreSQL using raw queries.

---

## Tech Stack

* FastAPI
* asyncpg
* PostgreSQL
* Uvicorn

---

## Features

* Raw material management
* Inventory tracking
* Product management
* Sales order handling
* Basic dashboard analytics

---

## Project Structure

```
.
├── main.py
└── README.md
```

---

## Getting Started

### Prerequisites

* Python 3.8+
* PostgreSQL running locally

---

### Installation

Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

Install dependencies:

```bash
pip install fastapi uvicorn asyncpg
```

---

### Database Configuration

The application uses the following database configuration:

```
Host: localhost
Port: 5432
User: postgres
Password: root
Database: postgres
```

Update the configuration in `main.py` if needed.

---

### Database Setup

Run the following SQL queries to create required tables:

```sql
CREATE TABLE raw_materials (
    id SERIAL PRIMARY KEY,
    name TEXT,
    unit TEXT,
    cost_per_unit FLOAT
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    raw_material_id INT,
    lot_number TEXT,
    expiry_date TEXT,
    quantity FLOAT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    batch_size FLOAT
);

CREATE TABLE sales_orders (
    id SERIAL PRIMARY KEY,
    customer_name TEXT,
    quantity FLOAT,
    price FLOAT,
    discount FLOAT,
    final_total FLOAT
);
```

---

### Running the Application

Start the server:

```bash
uvicorn main:app --reload
```

Access API documentation:

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Raw Materials

* `POST /raw-materials`
* `GET /raw-materials`

### Inventory

* `POST /inventory`
* `GET /inventory`

### Products

* `POST /products`
* `GET /products`

### Sales

* `POST /sales`
* `GET /sales`

### Dashboard

* `GET /dashboard`

---

## Core Design

The project uses a reusable query execution function:

```python
async def execute_query(query: str, *args, fetch: bool = False)
```

* Uses positional parameters (`$1`, `$2`, etc.)
* Supports both read and write operations
* Works with connection pooling via asyncpg

---

## Limitations

This is a demo project and does not include:

* Authentication or authorization
* Input validation using Pydantic
* Transaction management
* Advanced business logic (production, BOM, stock deduction)
* Error handling layers

---

## Future Improvements

* Add production module with raw material consumption
* Implement profit and cost tracking
* Introduce Pydantic schemas for validation
* Add authentication (JWT)
* Structure project into services and modules
* Add database migrations

---

## License

This project is for learning and demonstration purposes.
