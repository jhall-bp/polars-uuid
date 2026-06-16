import polars as pl

from polars_uuid import uuid_v8_from_bytes

UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"


def test_uuid_v8() -> None:
    df = pl.select(index=pl.arange(1_000_000, eager=False), eager=False).select(
        pl.col("index").cast(pl.Binary)
    ).with_columns(
        uuid_v8_from_bytes("index").alias("uuid")
    ).collect()

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    # assert df["uuid"].str.contains(UUID_PATTERN).all()
