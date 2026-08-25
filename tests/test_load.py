"""Day 2 tests — load raw files into DuckDB. No S3 required (uses local fixtures)."""

from __future__ import annotations

from pathlib import Path

import duckdb

from de_pipeline import load


def test_load_orders_creates_table(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> None:
    count = load.load_orders(con, raw_dir=raw_dir)
    assert count == 6  # the sample fixture has 6 order rows
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert "raw_orders" in tables


def test_load_customers_creates_table(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> None:
    count = load.load_customers(con, raw_dir=raw_dir)
    assert count == 3  # the sample fixture has 3 customers
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    assert "raw_customers" in tables


def test_load_all_returns_counts(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> None:
    counts = load.load_all(con, raw_dir=raw_dir)
    assert counts == {"raw_orders": 6, "raw_customers": 3}
