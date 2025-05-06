import polars as pl
import pytest

from polars_uuid import uuid_v7, uuid_v7_now, uuid_v7_single

UUID_PATTERN = r"^[0-9a-f]{8}(?:\-[0-9a-f]{4}){3}-[0-9a-f]{12}$"


@pytest.fixture
def timestamp() -> float:
    return 123456789.000001234


@pytest.mark.parametrize(
    "timestamp",
    (123_456_789.000001234, 1_746_494_082.4762812, 946_684_800, 0)
)
def test_uuid_v7(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(100_000))}).with_columns(
        uuid=uuid_v7(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df["uuid"].str.contains(UUID_PATTERN).all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.slice(0, 15).n_unique() == 1


def test_uuid_v7_single(timestamp: float) -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(
        uuid=uuid_v7_single(timestamp=timestamp)
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].n_unique() == 1
    assert df["uuid"].str.contains(UUID_PATTERN).all()
    assert df["uuid"].str.slice(0, 15).n_unique() == 1


def test_uuid_v7_now() -> None:
    df = pl.DataFrame({"idx": list(range(1_000_000))}).with_columns(uuid=uuid_v7_now())

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df["uuid"].str.contains(UUID_PATTERN).all()
    assert df["uuid"].is_sorted()
    assert df["uuid"].str.slice(0, 15).n_unique() > 1
