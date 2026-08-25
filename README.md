# Week 1 — Your First Data Pipeline

Welcome to Intro to Data Engineering. This week you build a small but real
pipeline: pull raw files out of object storage (S3), land them in an analytical
database (DuckDB), and shape them into something useful.

```
  S3 / RustFS            DuckDB                 DuckDB
 ┌────────────┐  fetch  ┌──────────┐  transform ┌──────────────────────┐
 │ orders.csv │ ──────► │ raw_*    │ ─────────► │ clean_orders          │
 │ customers… │         │ tables   │            │ customer_order_summary│
 └────────────┘         └──────────┘            └──────────────────────┘
     (Day 1)              (Day 2)                  (Day 2 / Day 3)
```

You'll fill in four small modules under `src/de_pipeline/`. Everything else
(the object store, the data, the config, the tests) is set up for you.

## What's in this repo

| Path | What it is |
| --- | --- |
| `docker-compose.yml` | A local, S3-compatible object store ([RustFS](https://rustfs.com)). |
| `scripts/generate_data.py` | Generates the synthetic source data (~30k orders + 4k customers). |
| `scripts/seed_s3.py` | Uploads that data into the S3 bucket. |
| `src/de_pipeline/config.py` | S3 settings + a ready-to-use client. **Provided — don't change.** |
| `src/de_pipeline/fetch.py` | **Day 1, you write this** — download from S3. |
| `src/de_pipeline/load.py` | **Day 2, you write this** — load into DuckDB. |
| `src/de_pipeline/transform.py` | **Day 2/3, you write this** — clean + join. |
| `src/de_pipeline/pipeline.py` | **Day 3, you write this** — wire it all together. |
| `tests/` | Tests that pass as you implement each stage. |

## One-time setup

You need [`uv`](https://docs.astral.sh/uv/) and Docker installed. **Do these in
order, and confirm each one worked before moving to the next** — later steps
depend on earlier ones.

**1. Create the Python environment**

```bash
uv sync
```

> _Confirm:_ it finishes without errors and a `.venv/` folder now exists.

**2. Create your `.env`**

```bash
cp .env.example .env
```

> _Confirm:_ a `.env` file now exists. The defaults already match
> `docker-compose.yml`, so you don't need to edit it.

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

**5. Upload the data into S3** (needs step 3 *and* step 4 done first)

```bash
uv run python scripts/seed_s3.py
```

> _Confirm:_ it prints `uploaded ... orders.csv` and `uploaded ... customers.json`.
> If you get a connection error instead, RustFS isn't up — go back to step 3.
> Then open the console at http://localhost:9001 and look in the `raw` bucket;
> both files should be there.

### VS Code

When you open this folder, VS Code will offer to install the recommended
extensions (Python + **Ruff**). Say yes. After that:

- **Ruff** highlights style/lint problems inline as you type — fix the squiggles
  yourself (we intentionally don't auto-fix on save).
- The **Testing** panel (the beaker icon) discovers the tests so you can run or
  debug them with a click instead of the terminal.

## The week, day by day

**The rhythm all week: write one function → run its test → get it green → move to
the next.** Each step below gives you the exact test to run. A green test is your
signal to go on; a red one tells you what's still wrong. Get used to this loop —
it's how professional data engineers work.

> Sanity check first. Before you've written anything, run `uv run pytest`. Most
> tests fail with `NotImplementedError` — that's expected. Your whole job this
> week is turning them green, one at a time.

### Day 1 — first S3 touch (`fetch.py`)
Goal: pull the two source files down from S3 into `data/raw/`.
**Requires setup steps 3 + 5 (RustFS up and seeded).**

1. Implement `fetch_object()`, then `fetch_all()`.
2. **Checkpoint:**
   ```bash
   uv run pytest tests/test_fetch.py
   ```
   Green means you really pulled the files from S3. (If it says `skipped`, RustFS
   isn't reachable — start it and seed first.)
3. See it for real:
   ```bash
   uv run python -m de_pipeline.fetch
   ```

### Day 2 — fighting the data (`load.py`, start `transform.py`)
Goal: land both files in DuckDB tables, then write your first transform. These
tests use small built-in sample data, so **they don't need S3** — they run
anywhere. This is where **ETL vs. ELT** gets real: you *load first*, then
*transform in the warehouse*.

1. Implement `connect()` + `load_orders()`. **Checkpoint:**
   ```bash
   uv run pytest tests/test_load.py::test_load_orders_creates_table
   ```
2. Implement `load_customers()`. **Checkpoint:**
   ```bash
   uv run pytest tests/test_load.py::test_load_customers_creates_table
   ```
3. Implement `load_all()`. **Checkpoint:**
   ```bash
   uv run pytest tests/test_load.py::test_load_all_returns_counts
   ```
4. Move to `transform.py` and implement `clean_orders()`. **Checkpoint:**
   ```bash
   uv run pytest tests/test_transform.py::test_clean_orders_drops_unusable_and_types_date
   ```

> Tip: a whole file at once works too — `uv run pytest tests/test_load.py`.

### Day 3 — finish + structured vs. semi-structured (`transform.py`, `pipeline.py`)

1. Implement `customer_order_summary()`. **Checkpoint:**
   ```bash
   uv run pytest tests/test_transform.py::test_customer_order_summary_is_one_row_per_customer
   ```
2. Implement `run_transforms()`, then `main()` in `pipeline.py` to wire
   `fetch → load → transform` into one run.
3. **Final checkpoint** — the whole suite green (RustFS up + seeded):
   ```bash
   uv run pytest
   ```
   then run the real pipeline end to end over all 30k rows:
   ```bash
   uv run de-pipeline
   ```
4. Update this README's notes (below), commit your work, and push to your branch.

> **Structured vs. semi-structured:** notice that `orders.csv` is neatly tabular
> (structured), while `customers.json` has a nested `address` object and a `tags`
> list (semi-structured). Part of the job is making the second one play nicely
> with the first.

## Working commands

```bash
uv run pytest                  # run the whole suite
uv run pytest tests/test_load.py   # run one file
uv run ruff check .            # lint (the same checks VS Code shows inline)
```

You can also run tests from VS Code's **Testing** panel instead of the terminal.

## How you'll know you're done

`uv run pytest` is green with RustFS running and the data seeded. The Day 1
fetch tests skip themselves when S3 isn't reachable, so don't be surprised if
they say `skipped` before you've started RustFS and seeded the data.

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

### Your notes (fill in on Day 3)

- What does your pipeline produce?
- One thing that was messier than expected:
- One thing you'd improve with more time:
