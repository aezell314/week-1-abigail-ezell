"""Combines the fetch, load, and transform stages into one end-to-end run.
"""

from __future__ import annotations

# The stages you'll orchestrate. Each exposes the functions you wrote this week.
from de_pipeline import fetch, load, transform  # noqa: F401


def main() -> None:
    """Runs the full pipeline end to end: fetches the source files, opens a DuckDB
    connection, loads the raw tables, runs the transforms, and prints a summary."""

    print("Fetching raw files...")
    paths = fetch.fetch_all()

    for name, path in paths.items():
        print(f"Successfully downloaded {name} to {path}")

    print("Loading raw files into a DuckDB warehouse...")
    con = load.connect()
    loads = load.load_all(con)
    for name, rows in loads.items():
        print(f"Successfully loaded table \'{name}\' with {rows} rows")

    print("Cleaning and aggregating raw data in DuckDB...")
    transforms = transform.run_transforms(con)
    for name, rows in transforms.items():
        print(f"Successfully loaded table \'{name}\' with {rows} rows")

if __name__ == "__main__":
    main()
