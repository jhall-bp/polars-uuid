import polars as pl

from polars_uuid import uuid_v4, uuid_v4_single

UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"


def test_uuid_v4() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(uuid=uuid_v4())

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df["uuid"].str.contains(UUID_PATTERN).all()


def test_partial_uuid_v4() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(
        pl.when(pl.col("idx") % 2 == 0).then(uuid_v4()).otherwise("idx").alias("uuid")
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df["uuid"].str.contains(UUID_PATTERN).sum() == (df.height / 2)
    assert df["uuid"].cast(pl.Int32, strict=False).null_count() == (df.height / 2)


def test_uuid_v4_single() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(uuid=uuid_v4_single())

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == 1
    assert df["uuid"].str.contains(UUID_PATTERN).all()


def test_partial_uuid_v4_single() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(
        pl.when(pl.col("idx") % 2 == 0).then(uuid_v4_single()).otherwise("idx").alias("uuid")
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].filter(df["uuid"].cast(pl.Int32, strict=False).is_null()).n_unique() == 1
    assert (df["uuid"].filter(df["uuid"].cast(pl.Int32, strict=False).is_null()).str.count_matches(UUID_PATTERN) == 1).all()
    assert df["uuid"].str.contains(UUID_PATTERN).sum() == (df.height / 2)
    assert df["uuid"].cast(pl.Int32, strict=False).null_count() == (df.height / 2)