import polars as pl
import pytest

from polars_uuid import is_uuid, uuid_v4, uuid_v7, uuid_v7_now


@pytest.mark.parametrize(
    "uuid_scalar_expr",
    [
        uuid_v4(scalar=True).alias("uuid"),
        uuid_v7_now(scalar=True).alias("uuid"),
        uuid_v7(timestamp=0, scalar=True).alias("uuid"),
    ],
)
def test_scalar_expressions_simple(uuid_scalar_expr: pl.Expr) -> None:
    df = (
        pl.DataFrame({"idx": list(range(1_000_000))})
        .with_columns(uuid=uuid_scalar_expr)
        .with_columns(is_uuid=is_uuid("uuid"))
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == 1
    assert df["is_uuid"].all()


@pytest.mark.parametrize(
    "uuid_scalar_expr",
    [
        uuid_v4(scalar=True).alias("uuid"),
        uuid_v7_now(scalar=True).alias("uuid"),
        uuid_v7(timestamp=0, scalar=True).alias("uuid"),
    ],
)
def test_scalar_expressions_group_by(uuid_scalar_expr: pl.Expr) -> None:
    first_letter_of_animal = pl.col("animal").str.head(1).alias("group")

    df = (
        pl.DataFrame({"animal": ["Aardvark", "Antelope", "Bear", "Beaver", "Cat"]})
        .group_by(first_letter_of_animal)
        .agg(
            pl.col("animal"),
            uuid_scalar_expr,
        )
        .explode("animal")
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == df["animal"].str.head(1).n_unique()

    df_grouped = df.group_by(first_letter_of_animal).all()
    assert (df_grouped["uuid"].list.n_unique() == 1).all()
    assert df_grouped["uuid"].list.first().n_unique() == df_grouped.height
