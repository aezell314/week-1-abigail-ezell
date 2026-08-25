"""Day 2/3 tests — transforms over the raw tables. No S3 required.

These use the ``loaded_con`` fixture, which already has raw_orders +
raw_customers populated, so they pass as soon as your transforms work — even if
load.py isn't finished yet.
"""

from __future__ import annotations

import duckdb

from de_pipeline import transform


def test_clean_orders_drops_unusable_and_types_date(loaded_con: duckdb.DuckDBPyConnection) -> None:
    rows = transform.clean_orders(loaded_con)
    # 2 of the 6 sample rows have a blank quantity or price and should be dropped.
    assert rows == 4

    # order_date should now be a real DATE type, not text.
    dtype = loaded_con.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = 'clean_orders' AND column_name = 'order_date'"
    ).fetchone()[0]
    assert "DATE" in dtype.upper()

    # status should be normalized (lower-cased, trimmed): no padded/upper values.
    rows_ = loaded_con.execute("SELECT DISTINCT status FROM clean_orders").fetchall()
    statuses = {r[0] for r in rows_}
    assert statuses == {s.strip().lower() for s in statuses}


def test_customer_order_summary_is_one_row_per_customer(
    loaded_con: duckdb.DuckDBPyConnection,
) -> None:
    transform.clean_orders(loaded_con)
    rows = transform.customer_order_summary(loaded_con)
    assert rows >= 1

    # No customer should appear twice.
    dupes = loaded_con.execute(
        "SELECT customer_id, count(*) FROM customer_order_summary "
        "GROUP BY customer_id HAVING count(*) > 1"
    ).fetchall()
    assert dupes == []
