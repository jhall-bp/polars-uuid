# Polars UUID

[![PyPI version](https://badge.fury.io/py/polars-uuid.svg)](https://badge.fury.io/py/polars-uuid)

Utilities for generating v4 and v7 UUIDs in `polars`.

## Use Case

I use `polars` as part of an ETL process to clean up and load data into DynamoDB. Each new record needs a synthetic ID, and using Python's `uuid` module with `polars`' `.map_elements()` expression was too slow.

## Examples

### Generate Random v4 UUIDs

```python
import polars as pl
import polars_uuid as pl_uuid

df = pl.DataFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]}).with_columns(
    pl_uuid.uuid_v4().alias("id")
)

print(df)
#  shape: (5, 2)
#  ┌──────────┬──────────────────────────────────────┐
#  │ animal   ┆ id                                   │
#  │ ---      ┆ ---                                  │
#  │ str      ┆ str                                  │
#  ╞══════════╪══════════════════════════════════════╡
#  │ Aardvark ┆ 3e5eec34-59f3-4a10-8808-b693b3e0e92c │
#  │ Bear     ┆ 1125682b-8bc9-4b5b-85af-2345b6c2a85a │
#  │ Cat      ┆ cc4e6620-dba9-4b58-8814-b09d37ca748a │
#  │ Dog      ┆ ac38f738-7c74-4aaa-afcd-4534f16472a6 │
#  │ Emu      ┆ f8657b99-692c-438e-ba21-daf0d80e5e89 │
#  └──────────┴──────────────────────────────────────┘
```

### Generate v7 UUIDs Based on the Current Time

```python
df = pl.DataFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]}).with_columns(
    pl_uuid.uuid_v7_now().alias("id")
)

print(df)
#  shape: (5, 2)
#  ┌──────────┬──────────────────────────────────────┐
#  │ animal   ┆ id                                   │
#  │ ---      ┆ ---                                  │
#  │ str      ┆ str                                  │
#  ╞══════════╪══════════════════════════════════════╡
#  │ Aardvark ┆ 0198062f-47b7-74d2-8d59-abc7dd3b30ea │
#  │ Bear     ┆ 0198062f-47b7-74d2-8d59-abd32466c6e0 │
#  │ Cat      ┆ 0198062f-47b7-74d2-8d59-abe5412a42c2 │
#  │ Dog      ┆ 0198062f-47b7-74d2-8d59-abf3655347a2 │
#  │ Emu      ┆ 0198062f-47b7-74d2-8d59-ac0e6611e60b │
#  └──────────┴──────────────────────────────────────┘
```

### Generate a Random UUID for Each Group of Items

```python
df = (
    pl.DataFrame({"animal": ["Aardvark", "Antelope", "Bear", "Beaver", "Cat"]})
    .group_by(pl.col("animal").str.head(1).alias("group"))
    .agg(pl.col("animal"))
    .with_columns(pl_uuid.uuid_v4().alias("id"))
    .explode("animal")
)

print(df)
#  shape: (5, 3)
#  ┌───────┬──────────┬──────────────────────────────────────┐
#  │ group ┆ animal   ┆ id                                   │
#  │ ---   ┆ ---      ┆ ---                                  │
#  │ str   ┆ str      ┆ str                                  │
#  ╞═══════╪══════════╪══════════════════════════════════════╡
#  │ C     ┆ Cat      ┆ 93caaad7-0dad-403c-ae02-4bde1cdf6bed │
#  │ B     ┆ Bear     ┆ 4de0c824-7d9b-4855-adad-bc6c4e710ef1 │
#  │ B     ┆ Beaver   ┆ 4de0c824-7d9b-4855-adad-bc6c4e710ef1 │
#  │ A     ┆ Aardvark ┆ 09fb670a-c4a1-4cc0-bc42-9d923653667c │
#  │ A     ┆ Antelope ┆ 09fb670a-c4a1-4cc0-bc42-9d923653667c │
#  └───────┴──────────┴──────────────────────────────────────┘
```

## Lazy Frames

`polars_uuid` works well with lazy frames, but it is important to keep in mind that the generated UUIDs will be different each time a lazy frame is collected.

Random UUID expressions are evaluated independently, including separate columns
and queries passed to `pl.collect_all`. To share generated IDs across query
branches, collect the UUID-bearing frame once and branch from that result.

Use `scalar=True` to generate one UUID per query, or one per group inside
`group_by().agg()` or `.over()`. Scalar generation can require an in-memory
fallback. When you need one UUID per output group, the example above generates
IDs after aggregation, avoiding that additional fallback. Other operations,
including list aggregation, may still require an in-memory fallback.

For example:

```python
lf = pl.LazyFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]}).with_columns(
    pl_uuid.uuid_v7_now().alias("id")
)

df_a = lf.collect()
df_b = lf.collect()

df_ab = df_a.join(df_b, on="id", how="inner", validate="1:1")
print(df_ab)
# shape: (0, 3)
# ┌────────┬─────┬──────────────┐
# │ animal ┆ id  ┆ animal_right │
# │ ---    ┆ --- ┆ ---          │
# │ str    ┆ str ┆ str          │
# ╞════════╪═════╪══════════════╡
# └────────┴─────┴──────────────┘
#
# Empty because the generated IDs are different each time lf is collected!
```

## Benchmarks

<details>
<summary>Environment and methodology</summary>

Measured on 23 October 2026 on an Apple M4 Pro (12 CPU cores, 24 GiB RAM),
running macOS 27.0.1 and CPython 3.15.0. Dependencies were Polars 2.0.0,
DuckDB 2.0.0, and PyArrow 26.0.0, with a local release build of
`polars-uuid` 0.9.0 from source commit `13f5549`.

Each script ran once, sequentially, with one untimed warm-up per method and
both engines configured for 12 threads. Times are total elapsed seconds for
the stated iteration count, including query execution, UUID string formatting,
and Arrow materialization. All methods produce Arrow tables with UUID strings.
The generators retain their libraries' native randomness and, for UUIDv7,
timestamp sampling and ordering behavior.

</details>

### Generate an Arrow Table with 100,000 UUIDv4 Values

Each iteration generates an integer index and 100,000 UUID strings.

| Method | Time (1,000 iterations) | Relative to `polars_uuid` |
| --- | ---: | ---: |
| `polars_uuid.uuid_v4()` | 1.158 s | Baseline |
| Python `uuid.uuid4()` + `map_batches` | 132.434 s | 114.3× slower |
| DuckDB `uuidv4()` | 2.332 s | 2.0× slower |

See [UUIDv4 generation benchmark](benchmarks/uuid4_generation.py).

### Generate an Arrow Table with 100,000 UUIDv7 Values

Each iteration generates an integer index and 100,000 UUID strings using the
current time.

| Method | Time (1,000 iterations) | Relative to `polars_uuid` |
| --- | ---: | ---: |
| `polars_uuid.uuid_v7_now()` | 1.250 s | Baseline |
| Python `uuid.uuid7()` + `map_batches` | 153.820 s | 123.1× slower |
| DuckDB `uuidv7()` | 2.994 s | 2.4× slower |

See [UUIDv7 generation benchmark](benchmarks/uuid7_generation.py).
