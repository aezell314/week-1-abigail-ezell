"""Day 2/3 — transform the raw tables into something useful.

The raw tables are messy on purpose:
  - raw_orders has a text ``order_date`` like "05-Jan-2024" (DuckDB leaves it as
    text), a ``status`` with mixed casing and stray spaces, and some rows with a
    blank quantity or price.
  - raw_customers is semi-structured JSON: each customer has a nested ``address``
    object and a ``tags`` list.

Write SQL against the connection to clean and combine this data. Start small,
get one transform green, then build up. (Week 2's theme is "your transforms are
basic, let's get serious" — so basic is fine now.)

Docs:
  - DuckDB SQL introduction:  https://duckdb.org/docs/stable/sql/introduction
  - date formats (strptime):  https://duckdb.org/docs/stable/sql/functions/dateformat
  - aggregates & GROUP BY:    https://duckdb.org/docs/stable/sql/query_syntax/groupby
"""

from __future__ import annotations

import duckdb


def clean_orders(con: duckdb.DuckDBPyConnection) -> int:
    """Build a ``clean_orders`` table from ``raw_orders`` and return its row count.

    ``clean_orders`` should: turn the text ``order_date`` into a real DATE,
    normalize ``status`` to lower-case with surrounding spaces removed, add a
    ``line_total`` column (quantity * price), and drop rows that are missing a
    quantity or price."""
    raise NotImplementedError("Day 2/3: implement clean_orders()")


def customer_order_summary(con: duckdb.DuckDBPyConnection) -> int:
    """Build a ``customer_order_summary`` table with one row per customer —
    ``customer_id``, ``name``, ``order_count``, ``total_revenue`` — by joining
    ``clean_orders`` to ``raw_customers``. Return its row count."""
    raise NotImplementedError("Day 2/3: implement customer_order_summary()")


def run_transforms(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Run every transform in order and return ``{table_name: row_count}``."""
    raise NotImplementedError("Day 2/3: implement run_transforms()")
