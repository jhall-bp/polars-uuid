# /// script
# requires-python = ">=3.14"
# dependencies = [
#   "polars-uuid",
#   "polars",
#   "duckdb",
#   "pyarrow",
# ]
# ///

from __future__ import annotations

import timeit
import uuid

import duckdb
import polars as pl

from polars_uuid import uuid_v4


ITERATIONS = 1_000
ROW_COUNT = 100_000
DUCKDB_CONNECTION = duckdb.connect(database=":memory:")


def run_python_uuid() -> None:
    (
        pl.select(idx=pl.arange(0, ROW_COUNT), eager=False)
        .with_columns(id=pl.first().map_elements(lambda _: str(uuid.uuid4()), return_dtype=pl.String))
        .collect()
        .to_arrow()
    )


def run_polars_uuid() -> None:
    (
        pl.select(idx=pl.arange(0, ROW_COUNT), eager=False)
        .with_columns(uuid=uuid_v4())
        .collect()
        .to_arrow()
    )


def run_duckdb() -> None:
    DUCKDB_CONNECTION.execute(
        f"""
        SELECT
            idx,
            uuid() AS uuid
        FROM range({ROW_COUNT}) AS t(idx)
        """
    ).to_arrow_table()


if __name__ == "__main__":
    python_seconds = timeit.timeit(run_python_uuid, number=ITERATIONS)
    polars_seconds = timeit.timeit(run_polars_uuid, number=ITERATIONS)
    duckdb_seconds = timeit.timeit(run_duckdb, number=ITERATIONS)

    print(f"python_uuid: {python_seconds:.6f} seconds")
    print(f"polars_uuid: {polars_seconds:.6f} seconds")
    print(f"duckdb:      {duckdb_seconds:.6f} seconds")
