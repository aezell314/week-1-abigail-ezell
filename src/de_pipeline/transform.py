"""Transforms the raw tables into analytics-ready data.

Docs:
  - DuckDB SQL introduction:  https://duckdb.org/docs/stable/sql/introduction
  - date formats (strptime):  https://duckdb.org/docs/stable/sql/functions/dateformat
  - aggregates & GROUP BY:    https://duckdb.org/docs/stable/sql/query_syntax/groupby
"""

from __future__ import annotations

import duckdb

from de_pipeline.load import connect


def clean_orders(con: duckdb.DuckDBPyConnection) -> int:
    """Builds a ``clean_orders`` table from ``raw_orders`` and returns its row count.

    ``clean_orders`` turns the text ``order_date`` into a real DATE,
    normalizes ``status`` to lower-case with surrounding spaces removed, adds a
    ``line_total`` column (quantity * price), and drops rows that are missing a
    quantity or price."""
    con.execute("""
      CREATE OR REPLACE TABLE clean_orders AS
      SELECT order_id,
            customer_id,
            sku,
            quantity,
            price,
            trim(lower(status)) as status,
            strptime(order_date, '%d-%b-%Y')::DATE as order_date,
            quantity*price as line_total
      FROM raw_orders
      where quantity is not null and price is not null;
    """)
    num_rows = con.execute("select count(*) from clean_orders;").fetchone()[0]
    return num_rows


def customer_order_summary(con: duckdb.DuckDBPyConnection) -> int:
    """Builds a ``customer_order_summary`` table with one row per customer —
    ``customer_id``, ``name``, ``order_count``, ``total_revenue`` — by joining
    ``clean_orders`` to ``raw_customers``. Returns its row count."""
    con.execute("""
      CREATE OR REPLACE TABLE customer_order_summary AS
      SELECT c.customer_id,
            c.name,
            count(o.order_id) as order_count,
            sum(o.line_total) as total_revenue
      FROM raw_customers c
      left join clean_orders o
      using(customer_id)
      group by all
      ;
    """)
    num_rows = con.execute("select count(*) from customer_order_summary;").fetchone()[0]
    return num_rows


def run_transforms(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Runs every transform in order and returns ``{table_name: row_count}``."""
    cleanorders = clean_orders(con)
    custordersum = customer_order_summary(con)
    return {
      'clean_orders':cleanorders,
      'customer_order_summary':custordersum
      }
