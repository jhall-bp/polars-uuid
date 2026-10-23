# /// script
# requires-python = ">=3.15"
# dependencies = [
#   "polars-uuid==0.9.0",
#   "polars==2.0.0",
#   "duckdb==2.0.0",
#   "pyarrow",
# ]
# ///

from __future__ import annotations

import timeit
import uuid

import duckdb
import polars as pl

from polars_uuid import uuid_v7_now

ITERATIONS = 1_000
ROW_COUNT = 100_000
DUCKDB_CONNECTION = duckdb.connect(config={"threads": pl.thread_pool_size()})

# All methods materialize an Arrow table with an integer index and UUID strings.
# These timings compare each library's native "now" generator; timestamp sampling
# and ordering guarantees can differ between implementations.


def run_python_uuid() -> None:
    (
        pl.select(idx=pl.arange(0, ROW_COUNT, eager=False), eager=False)
        .with_columns(
            uuid=pl.first().map_batches(
                lambda s: pl.Series(None, [str(uuid.uuid7()) for _ in range(s.len())]),
                return_dtype=pl.String,
            )
        )
        .collect()
        .to_arrow()
    )


def run_polars_uuid() -> None:
    (
        pl.select(idx=pl.arange(0, ROW_COUNT, eager=False), eager=False)
        .with_columns(uuid=uuid_v7_now())
        .collect()
        .to_arrow()
    )


def run_duckdb() -> None:
    DUCKDB_CONNECTION.sql(
        f"""
        SELECT
            idx,
            uuidv7()::VARCHAR AS uuid
        FROM range({ROW_COUNT}) AS t(idx)
        """
    ).to_arrow_table()


if __name__ == "__main__":
    # Warm up imports, the plugin, and both engines before measuring any method.
    run_python_uuid()
    run_polars_uuid()
    run_duckdb()

    python_seconds = timeit.timeit(run_python_uuid, number=ITERATIONS)
    polars_seconds = timeit.timeit(run_polars_uuid, number=ITERATIONS)
    duckdb_seconds = timeit.timeit(run_duckdb, number=ITERATIONS)

    print(f"python_uuid: {python_seconds:.6f} seconds")
    print(f"polars_uuid: {polars_seconds:.6f} seconds")
    print(f"duckdb:      {duckdb_seconds:.6f} seconds")
