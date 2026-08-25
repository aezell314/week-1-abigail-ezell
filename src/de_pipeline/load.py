"""Day 2 — load the raw files into DuckDB.

Open a DuckDB database (one file the whole pipeline shares) and load each local
raw file into its own table:
    data/raw/orders.csv      -> table ``raw_orders``
    data/raw/customers.json  -> table ``raw_customers``

ETL vs. ELT: right now you're landing the data *as-is* (Extract, Load). The
reshaping happens later in transform.py (Transform) — that's the "EL" of ELT.

Docs:
  - DuckDB Python API:   https://duckdb.org/docs/stable/clients/python/overview
  - reading CSV files:   https://duckdb.org/docs/stable/data/csv/overview
  - reading JSON files:  https://duckdb.org/docs/stable/data/json/overview
"""

from __future__ import annotations

from pathlib import Path

import duckdb

from de_pipeline.fetch import RAW_DIR

# The DuckDB database file the whole pipeline shares.
DB_PATH = Path("data/warehouse.duckdb")


def connect(db_path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    """Open (creating it if needed) the DuckDB database at ``db_path`` and return
    the connection."""
    raise NotImplementedError("Day 2: implement connect()")


def load_orders(con: duckdb.DuckDBPyConnection, raw_dir: Path = RAW_DIR) -> int:
    """Load ``raw_dir/orders.csv`` into a table named ``raw_orders``. Return the
    number of rows loaded."""
    raise NotImplementedError("Day 2: implement load_orders()")


def load_customers(con: duckdb.DuckDBPyConnection, raw_dir: Path = RAW_DIR) -> int:
    """Load ``raw_dir/customers.json`` into a table named ``raw_customers``.
    Return the number of rows loaded."""
    raise NotImplementedError("Day 2: implement load_customers()")


def load_all(con: duckdb.DuckDBPyConnection, raw_dir: Path = RAW_DIR) -> dict[str, int]:
    """Load both files and return ``{table_name: row_count}`` — i.e.
    ``{"raw_orders": ..., "raw_customers": ...}``."""
    raise NotImplementedError("Day 2: implement load_all()")


if __name__ == "__main__":
    # uv run python -m de_pipeline.load
    con = connect()
    print("loaded:", load_all(con))
