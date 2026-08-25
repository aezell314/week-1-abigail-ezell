"""Shared pytest fixtures.

These build tiny local fixtures so the load/transform tests run WITHOUT needing
S3 or the full 30k-row dataset. They mirror the shape of the real source files.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest

# A handful of rows that mimic the real data, including the messy bits:
# a blank quantity, a blank price, and mixed-case / padded status values.
SAMPLE_ORDERS_CSV = """order_id,customer_id,sku,quantity,price,status,order_date
1,1,WIDGET-01,2,12.50,completed,05-Jan-2024
2,1,GADGET-07,1,42.99,Completed,11-Feb-2024
3,2,CABLE-USB,3,9.99,SHIPPED,02-Mar-2024
4,2,WIDGET-02,,18.00, Pending ,20-Mar-2024
5,3,MOUNT-PRO,1,,shipped,01-Apr-2024
6,3,SPROCKET-3,2,99.00,cancelled,15-May-2024
"""

SAMPLE_CUSTOMERS = [
    {
        "customer_id": 1,
        "name": "Ava Reyes",
        "email": "user1@example.com",
        "signup_date": "2023-04-10",
        "address": {"city": "Nashville", "state": "TN", "zip": "37206"},
        "tags": ["vip", "newsletter"],
    },
    {
        "customer_id": 2,
        "name": "Liam Tran",
        "email": "user2@example.com",
        "signup_date": "2023-09-01",
        "address": {"city": "Austin", "state": "TX", "zip": "78704"},
        "tags": ["new"],
    },
    {
        "customer_id": 3,
        "name": "Maya Patel",
        "email": "user3@example.com",
        "signup_date": "2024-01-15",
        "address": {"city": "Denver", "state": "CO", "zip": "80205"},
        "tags": [],
    },
]


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    """A temp directory holding tiny orders.csv + customers.json fixtures."""
    (tmp_path / "orders.csv").write_text(SAMPLE_ORDERS_CSV)
    (tmp_path / "customers.json").write_text(json.dumps(SAMPLE_CUSTOMERS, indent=2))
    return tmp_path


@pytest.fixture
def con() -> duckdb.DuckDBPyConnection:
    """An in-memory DuckDB connection."""
    connection = duckdb.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def loaded_con(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> duckdb.DuckDBPyConnection:
    """A DuckDB connection with raw_orders + raw_customers already populated.

    Useful for transform tests so they don't depend on load.py being finished.
    """
    con.execute(
        "CREATE TABLE raw_orders AS SELECT * FROM read_csv_auto(?)",
        [str(raw_dir / "orders.csv")],
    )
    con.execute(
        "CREATE TABLE raw_customers AS SELECT * FROM read_json_auto(?)",
        [str(raw_dir / "customers.json")],
    )
    return con
