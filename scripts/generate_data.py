"""Generate the synthetic source data for Week 1.

Produces two files under ``data/source/``:

  - orders.csv      ~30,000 rows of e-commerce orders (structured, tabular).
                    Deliberately a little messy: text dates, mixed-case status,
                    and a sprinkling of blank quantity/price cells.
  - customers.json  ~4,000 customers (semi-structured): each record has a nested
                    ``address`` object and a ``tags`` list.

Everything is seeded, so re-running gives identical files. No third-party
dependencies — standard library only.

Run it with:  uv run python scripts/generate_data.py
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

N_ORDERS = 30_000
N_CUSTOMERS = 4_000
SEED = 42

OUT_DIR = Path("data/source")

FIRST_NAMES = [
    "Ava",
    "Liam",
    "Maya",
    "Noah",
    "Zoe",
    "Ethan",
    "Iris",
    "Owen",
    "Nora",
    "Leo",
    "Ruby",
    "Eli",
    "June",
    "Max",
    "Cora",
    "Finn",
    "Hazel",
    "Jude",
]
LAST_NAMES = [
    "Reyes",
    "Tran",
    "Patel",
    "Nguyen",
    "Walsh",
    "Kim",
    "Okafor",
    "Diaz",
    "Cohen",
    "Ross",
    "Mbeki",
    "Sato",
    "Flores",
    "Park",
    "Haddad",
    "Novak",
]
CITIES = [
    ("Nashville", "TN"),
    ("Austin", "TX"),
    ("Denver", "CO"),
    ("Portland", "OR"),
    ("Atlanta", "GA"),
    ("Boston", "MA"),
    ("Chicago", "IL"),
    ("Seattle", "WA"),
]
PRODUCTS = [
    ("WIDGET-01", 12.50),
    ("WIDGET-02", 18.00),
    ("GADGET-07", 42.99),
    ("GADGET-12", 7.25),
    ("SPROCKET-3", 99.00),
    ("SPROCKET-9", 145.50),
    ("CABLE-USB", 9.99),
    ("CABLE-HDMI", 14.49),
    ("MOUNT-PRO", 31.00),
    ("MOUNT-LITE", 22.75),
]
# Mixed casing + whitespace on purpose, so students have something to normalize.
STATUSES = ["completed", "Completed", "SHIPPED", "shipped", "pending", " Pending ", "cancelled"]
TAG_POOL = ["new", "vip", "wholesale", "newsletter", "churn-risk", "referral"]


def generate_customers(rng: random.Random) -> list[dict]:
    customers = []
    for cid in range(1, N_CUSTOMERS + 1):
        city, state = rng.choice(CITIES)
        customers.append(
            {
                "customer_id": cid,
                "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "email": f"user{cid}@example.com",
                "signup_date": str(date(2023, 1, 1) + timedelta(days=rng.randint(0, 700))),
                "address": {
                    "city": city,
                    "state": state,
                    "zip": f"{rng.randint(10000, 99999)}",
                },
                "tags": rng.sample(TAG_POOL, k=rng.randint(0, 3)),
            }
        )
    return customers


def generate_orders(rng: random.Random) -> list[dict]:
    start = date(2024, 1, 1)
    orders = []
    for oid in range(1, N_ORDERS + 1):
        sku, base_price = rng.choice(PRODUCTS)
        # Text date in a format DuckDB won't auto-detect (e.g. "05-Jan-2024"),
        # so it lands as VARCHAR and Day 2/3 has real parsing to do.
        order_day = start + timedelta(days=rng.randint(0, 364))
        order_date = order_day.strftime("%d-%b-%Y")

        quantity: object = rng.randint(1, 6)
        price: object = round(base_price * rng.uniform(0.9, 1.1), 2)
        # ~1.5% of rows have a missing quantity or price for cleaning practice.
        if rng.random() < 0.015:
            quantity = ""
        if rng.random() < 0.015:
            price = ""

        orders.append(
            {
                "order_id": oid,
                "customer_id": rng.randint(1, N_CUSTOMERS),
                "sku": sku,
                "quantity": quantity,
                "price": price,
                "status": rng.choice(STATUSES),
                "order_date": order_date,
            }
        )
    return orders


def main() -> None:
    rng = random.Random(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(rng)
    customers_path = OUT_DIR / "customers.json"
    with customers_path.open("w") as f:
        json.dump(customers, f, indent=2)

    orders = generate_orders(rng)
    orders_path = OUT_DIR / "orders.csv"
    fields = ["order_id", "customer_id", "sku", "quantity", "price", "status", "order_date"]
    with orders_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(orders)

    print(f"wrote {len(orders):,} orders   -> {orders_path}")
    print(f"wrote {len(customers):,} customers -> {customers_path}")


if __name__ == "__main__":
    main()
