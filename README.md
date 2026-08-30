# Building an ELT pipeline with mock customer and order data

The pipeline contained in this repo pulls raw files out of object storage (S3), lands them in an analytical
database (DuckDB), and shapes them a useful format. One file involved in this pipeline contains structured data, while the other contains semi-structured JSON data.

```
  S3 / RustFS            DuckDB                 DuckDB
 ┌────────────┐  fetch  ┌──────────┐  transform ┌──────────────────────┐
 │ orders.csv │ ──────► │ raw_*    │ ─────────► │ clean_orders          │
 │ customers… │         │ tables   │            │ customer_order_summary│
 └────────────┘         └──────────┘            └──────────────────────┘
```

## What's in this repo

| Path | What it is |
| --- | --- |
| `docker-compose.yml` | A local, S3-compatible object store ([RustFS](https://rustfs.com)). |
| `scripts/generate_data.py` | Generates the synthetic source data (~30k orders + 4k customers). |
| `scripts/seed_s3.py` | Uploads that data into the S3 bucket. |
| `src/de_pipeline/config.py` | S3 settings + a ready-to-use client. |
| `src/de_pipeline/fetch.py` | This module downloads the two source files from S3 into `data/raw/`. |
| `src/de_pipeline/load.py` | This module loads each local raw file into its own DuckDB table. |
| `src/de_pipeline/transform.py` | This module cleans the orders data, joins it with the customer data, and aggregates the two to build a table showing total revenue per customer. |
| `src/de_pipeline/pipeline.py` | This module combines functions from config.py, fetch.py, load.py, and transform.py to implement the entire pipeline flow and prints useful output after each step. |
| `tests/` | Test files for each module in the pipeline. |

## One-time setup

You need [`uv`](https://docs.astral.sh/uv/) and Docker installed. 

**1. Create the Python environment**

```bash
uv sync
```

> _Confirm:_ it finishes without errors and a `.venv/` folder now exists.

**2. Create your `.env`**

```bash
cp .env.example .env
```

> _Confirm:_ a `.env` file now exists. 

**3. Start the local S3 store (RustFS)**

```bash
docker compose up -d
```

This runs the object store in the background (S3 API on
http://localhost:9000, web console on http://localhost:9001, login
`rustfsadmin` / `rustfsadmin`).

> _Confirm (the next steps need this running):_ wait ~20–30 seconds, then run
> `docker compose ps` and check the **STATUS** column shows `healthy`. You can
> also open http://localhost:9001 in a browser and log in.

**4. Generate the source data** (writes local files — no S3 yet)

```bash
uv run python scripts/generate_data.py
```

> _Confirm:_ it prints `wrote 30,000 orders` and `wrote 4,000 customers`, and
> `data/source/` now contains `orders.csv` and `customers.json`.

**5. Upload the data into S3** 

```bash
uv run python scripts/seed_s3.py
```

> _Confirm:_ it prints `uploaded ... orders.csv` and `uploaded ... customers.json`.
> If you get a connection error instead, RustFS isn't up — go back to step 3.
> Then open the console at http://localhost:9001 and look in the `raw` bucket;
> both files should be there.

**6. Run the ELT pipeline** 

As a final checkpoint, make sure the entire test suite passes:

```bash
uv run pytest
```

then run the real pipeline end to end over all 30k rows:

```bash
uv run de-pipeline
```

## Troubleshooting

- **`docker compose ps` shows `unhealthy` or `starting`** — give it 20–30 seconds
  after `up`; it takes a moment to come online. Check logs with
  `docker compose logs rustfs`.
- **Port 9000 or 9001 already in use** — something else (often another MinIO/S3
  or a local service) is on that port. Stop it, or change the left-hand number in
  `docker-compose.yml` (e.g. `"9100:9000"`) and update `S3_ENDPOINT_URL` in your
  `.env` to match.
- **`seed_s3.py` can't connect** — RustFS isn't up yet, or it's on a different
  port than your `.env` expects. Confirm setup step 3 first.
- **Windows users** — use `copy .env.example .env` instead of `cp`. If VS Code
  doesn't pick up the environment automatically, open the command palette →
  *Python: Select Interpreter* → choose the one under `.venv`.

---
