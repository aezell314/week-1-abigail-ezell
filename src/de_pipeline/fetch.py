"""Fetches the raw source files from S3 (RustFS).

Docs:
  - boto3 S3 client:     https://docs.aws.amazon.com/boto3/latest/reference/services/s3.html
  - downloading a file:  https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/download_file.html
"""

from __future__ import annotations

from pathlib import Path

from de_pipeline.config import get_s3_client, settings

# Where downloaded raw files land. (data/ is git-ignored.)
RAW_DIR = Path("data/raw")


def fetch_object(key: str, dest_dir: Path = RAW_DIR) -> Path:
    """Downloads the object ``key`` from the bucket into ``dest_dir``, and returns
    the local path it was written to."""
    client = get_s3_client()
    filename = dest_dir / key
    client.download_file(Bucket=settings.bucket,
                        Key=key,
                        Filename=filename)
    return filename


def fetch_all(dest_dir: Path = RAW_DIR) -> dict[str, Path]:
    """Downloads both source files and returns a mapping of name -> local path:
    ``{"orders": <path>, "customers": <path>}``.
    """
    return {'orders':fetch_object(key=settings.orders_key),
            'customers':fetch_object(key=settings.customers_key)}


if __name__ == "__main__":
    # Quick manual check:  uv run python -m de_pipeline.fetch
    paths = fetch_all()
    for name, path in paths.items():
        print(f"fetched {name} -> {path} ({path.stat().st_size:,} bytes)")
    print(f"bucket={settings.bucket} endpoint={settings.endpoint_url}")
