import polars as pl
from polars.testing import assert_frame_equal

from polars_uuid import uuid_v8_from_bytes, uuid_v8_by_hashing_str


def test_uuid_v8_from_binary() -> None:
    df = (
        pl.select(index=pl.arange(1_000_000, eager=False), eager=False)
        .select(pl.col("index").cast(pl.Binary))
        .with_columns(uuid_v8_from_bytes("index").alias("uuid"))
        .collect()
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()


def test_uuid_v8_by_hashing_str() -> None:
    df = (
        pl.select(index=pl.arange(1_000_000, eager=False), eager=False)
        .select(pl.col("index").cast(pl.String))
        .with_columns(uuid_v8_by_hashing_str("index").alias("uuid"))
        .collect()
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()


def test_uuid_v8_from_bytes_determinism() -> None:
    df1, df2 = pl.collect_all(
        (
            pl.select(index=pl.arange(1_000, eager=False), eager=False)
            .select(pl.col("index").cast(pl.Binary))
            .with_columns(uuid_v8_from_bytes("index").alias("uuid")),
            pl.select(index=pl.arange(1_000, eager=False), eager=False)
            .select(pl.col("index").cast(pl.Binary))
            .with_columns(uuid_v8_from_bytes("index").alias("uuid")),
        )
    )

    assert_frame_equal(df1, df2)


def test_uuid_v8_by_hashing_str_determinism() -> None:
    df1, df2 = pl.collect_all(
        (
            pl.select(index=pl.arange(1_000, eager=False), eager=False)
            .select(pl.col("index").cast(pl.String))
            .with_columns(uuid_v8_by_hashing_str("index").alias("uuid")),
            pl.select(index=pl.arange(1_000, eager=False), eager=False)
            .select(pl.col("index").cast(pl.String))
            .with_columns(uuid_v8_by_hashing_str("index").alias("uuid")),
        )
    )

    assert_frame_equal(df1, df2)
