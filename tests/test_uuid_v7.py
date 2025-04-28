import polars as pl
import pytest

from polars_uuid import uuid_v7, uuid_v7_now, uuid_v7_single

UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"


@pytest.fixture
def timestamp() -> float:
    return 1497624119.000001234


def test_uuid_v7(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(10_000_000))}).with_columns(
        uuid=uuid_v7(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert (df["uuid"].str.count_matches(UUID_PATTERN) == 1).all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.starts_with("015cb15a-86d8-7").all()


def test_uuid_v7_single(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(10_000_000))}).with_columns(
        uuid=uuid_v7_single(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert (df["uuid"].str.count_matches(UUID_PATTERN) == 1).all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.starts_with("015cb15a-86d8-7").all()


def test_uuid_v7_now() -> None:
    df = pl.DataFrame({"idx": list(range(10_000_000))}).with_columns(uuid=uuid_v7_now())

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert (df["uuid"].str.count_matches(UUID_PATTERN) == 1).all()
    assert df["uuid"].is_sorted()
