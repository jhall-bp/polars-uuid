import datetime

import hypothesis.strategies as st
import polars as pl
import pytest
from hypothesis import given
from polars.testing import assert_series_equal

from polars_uuid import (
    is_uuid,
    uuid_v7,
    uuid_v7_extract_dt,
    uuid_v7_now,
    uuid_v7_single,
)


@given(st.floats(min_value=0))
def test_uuid_v7(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(100_000))}).with_columns(
        uuid=uuid_v7(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df.select(is_uuid("uuid")).to_series().all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.slice(0, 15).n_unique() == 1


@given(st.floats(min_value=0))
def test_uuid_v7_single(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(100_000))}).with_columns(
        uuid=uuid_v7_single(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == 1
    assert df.select(is_uuid("uuid")).to_series().all()
    assert df["uuid"].str.slice(0, 15).n_unique() == 1


def test_uuid_v7_now() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(uuid=uuid_v7_now())

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df.select(is_uuid("uuid")).to_series().all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.slice(0, 15).n_unique() > 1


def test_uuid_v7_extract_dt() -> None:
    def py_extract_timestamp_from_uuidv7(uuid_str: str) -> int:
        hex_str = uuid_str.replace("-", "")
        if len(hex_str) != 32:
            raise ValueError("Invalid UUID string length.")

        timestamp_hex = hex_str[:12]
        return int(timestamp_hex, 16)

    df = (
        pl.DataFrame({"idx": list(range(100_000))})
        .with_columns(uuid=uuid_v7_now())
        .with_columns(
            dt=uuid_v7_extract_dt("uuid"),
            dt_py=pl.col("uuid")
            .map_elements(py_extract_timestamp_from_uuidv7, return_dtype=pl.Int64)
            .cast(pl.Datetime("ms", "UTC")),
        )
    )

    now = datetime.datetime.now(datetime.UTC)

    assert df["dt"].null_count() == 0
    assert df["dt"].dtype == pl.Datetime("ms", "UTC")
    assert (df["dt"] < now).all()

    assert df["dt_py"].null_count() == 0
    assert df["dt_py"].dtype == pl.Datetime("ms", "UTC")
    assert_series_equal(df["dt"], df["dt_py"], check_names=False)


def test_uuid_v7_extract_dt_strict_mode() -> None:
    with pytest.raises(
        pl.exceptions.ComputeError,
        match=r"Failed to extract timestamp from UUID string: .+$",
    ):
        df = (
            pl.DataFrame({"idx": list(range(100_000))})
            .with_columns(bad_uuid=pl.col("idx").cast(pl.String))
            .with_columns(dt=uuid_v7_extract_dt("bad_uuid"))
        )

    df = (
        pl.DataFrame({"idx": list(range(100_000))})
        .with_columns(bad_uuid=pl.col("idx").cast(pl.String))
        .with_columns(dt=uuid_v7_extract_dt("bad_uuid", strict=False))
    )

    assert df["dt"].dtype == pl.Datetime("ms", "UTC")
    assert df["dt"].null_count() == df.height
