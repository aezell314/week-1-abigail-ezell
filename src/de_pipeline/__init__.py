"""de_pipeline — your Week 1 data engineering pipeline.

The pipeline has four stages, one module each:

    fetch.py      Day 1  — pull the raw CSV + JSON down from S3 (RustFS)
    load.py       Day 2  — load both files into DuckDB
    transform.py  Day 2/3 — shape the raw tables into something useful
    pipeline.py   Day 3  — wire fetch -> load -> transform into one run

config.py is provided for you (S3 settings + client). Start in fetch.py.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
