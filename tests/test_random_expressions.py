import datetime
from typing import TYPE_CHECKING

import polars as pl
import pytest

from polars_uuid import uuid_v4, uuid_v7, uuid_v7_now

if TYPE_CHECKING:
    from polars._typing import EngineType


@pytest.fixture(
    params=[
        pytest.param(uuid_v4(), id="v4"),
        pytest.param(uuid_v4(scalar=True), id="v4_scalar"),
        pytest.param(uuid_v7_now(), id="v7_now"),
        pytest.param(uuid_v7_now(scalar=True), id="v7_now_scalar"),
        pytest.param(uuid_v7(timestamp=0), id="v7_timestamp"),
        pytest.param(uuid_v7(timestamp=0, scalar=True), id="v7_timestamp_scalar"),
        pytest.param(uuid_v7(timestamp="timestamp"), id="v7_dynamic"),
    ]
)
def uuid_expr(request: pytest.FixtureRequest) -> pl.Expr:
    return request.param


@pytest.fixture
def lf() -> pl.LazyFrame:
    return pl.LazyFrame(
        {"timestamp": [datetime.datetime(2000, 1, 1, tzinfo=datetime.UTC)] * 1_024}
    )


def test_random_expressions_in_independent_columns(
    lf: pl.LazyFrame, uuid_expr: pl.Expr, engine: EngineType
) -> None:
    df = lf.with_columns(a=uuid_expr, b=uuid_expr).collect(engine=engine)

    assert df.height == 1_024
    assert (df["a"] != df["b"]).all(ignore_nulls=False)


def test_random_expressions_in_independent_collections(
    lf: pl.LazyFrame, uuid_expr: pl.Expr, engine: EngineType
) -> None:
    query = lf.with_columns(uuid=uuid_expr)
    first, second = pl.collect_all([query, query], engine=engine)

    assert first.height == second.height == 1_024
    assert (first["uuid"] != second["uuid"]).all(ignore_nulls=False)
