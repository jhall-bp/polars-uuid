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

df = (
    pl.DataFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]})
    .with_columns(pl_uuid.uuid_v4().alias("id"))
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
df = (
    pl.DataFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]})
    .with_columns(pl_uuid.uuid_v7_now().alias("id"))
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
    .agg(
        pl.col("animal"),
        pl_uuid.uuid_v4(scalar=True).alias("id"),  # set scalar to True to generate a single UUID per group
    )
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

For example:

```python
lf = (
    pl.LazyFrame({"animal": ["Aardvark", "Bear", "Cat", "Dog", "Emu"]})
    .with_columns(pl_uuid.uuid_v7_now().alias("id"))
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

## Benchmark

### Generate a DataFrame with 10 000 UUIDv4 Values

| Method                  | Time (1 000 iterations) | Relative `polars_uuid` |
| ----------------------- | ----------------------- | ---------------------- |
| `polars_uuid`           | 2.34s                   | Baseline               |
| `uuid` + `map_elements` | 138.49s                 | 59.2x slower           |
| `duckdb`                | 1.95s                   | 1.2x faster            |

See [benchmarks](benchmarks/uuid4_generation.py) for more details.
