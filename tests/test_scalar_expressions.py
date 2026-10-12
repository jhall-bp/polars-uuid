from typing import TYPE_CHECKING

import polars as pl
import pytest

from polars_uuid import is_uuid, uuid_v4, uuid_v7, uuid_v7_now

if TYPE_CHECKING:
    from polars._typing import EngineType


@pytest.fixture(
    params=[
        pytest.param(uuid_v4(scalar=True), id="v4"),
        pytest.param(uuid_v7_now(scalar=True), id="v7_now"),
        pytest.param(uuid_v7(timestamp=0, scalar=True), id="v7_timestamp"),
    ]
)
def uuid_scalar_expr(request: pytest.FixtureRequest) -> pl.Expr:
    return request.param


@pytest.mark.parametrize("height", [0, 1, 1_024])
def test_scalar_expressions_simple(
    uuid_scalar_expr: pl.Expr, engine: EngineType, height: int
) -> None:
    lf = pl.LazyFrame({"idx": range(height)}).with_columns(uuid=uuid_scalar_expr)
    df = lf.collect(engine=engine)

    assert df.height == height
    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == min(height, 1)
    assert df.select(is_uuid("uuid")).to_series().all()
    if height:
        assert df["uuid"][0] != lf.collect(engine=engine)["uuid"][0]


@pytest.mark.parametrize("include_animals", [False, True])
def test_scalar_expressions_group_by(
    uuid_scalar_expr: pl.Expr, engine: EngineType, include_animals: bool
) -> None:
    animals = pl.Series(
        "animal",
        ["Aardvark", "Antelope", "Bear", "Beaver", "Cat", "Dog", "Dinosaur", "Emu"]
        * 128,
    ).shuffle(seed=0)
    # A list aggregation can trigger a different execution path from scalar-only agg.
    aggregations = [pl.col("animal")] if include_animals else []
    df = (
        pl.LazyFrame({"animal": animals})
        .group_by(pl.col("animal").str.head(1).alias("group"))
        .agg(*aggregations, uuid=uuid_scalar_expr)
        .collect(engine=engine)
    )

    assert df.height == 5
    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == 5


def test_scalar_expressions_window(
    uuid_scalar_expr: pl.Expr, engine: EngineType
) -> None:
    df = (
        pl.LazyFrame({"group": [0, 1, 2] * 512})
        .with_columns(uuid=uuid_scalar_expr.over("group"))
        .collect(engine=engine)
    )

    assert df.height == 1_536
    assert df["uuid"].null_count() == 0
    assert df["uuid"].n_unique() == 3
    assert (df.group_by("group").agg(pl.col("uuid").n_unique())["uuid"] == 1).all()
