import uuid

import polars as pl
from polars.testing import assert_series_equal

from polars_uuid import is_uuid, u64_pair_to_uuid, uuid_v4


def test_is_uuid() -> None:
    df = (
        pl.DataFrame({"idx": list(range(1_000_000))})
        .with_columns(uuid=uuid_v4(), null=pl.lit(None, dtype=pl.String))
        .with_columns(
            is_uuid=is_uuid("uuid"),
            is_not_uuid=is_uuid(pl.col("idx").cast(pl.String)),
            is_null=is_uuid("null"),
        )
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert df["is_uuid"].dtype == pl.Boolean
    assert df["is_uuid"].null_count() == 0
    assert df["is_uuid"].all()
    assert df["is_not_uuid"].dtype == pl.Boolean
    assert df["is_not_uuid"].null_count() == 0
    assert df["is_not_uuid"].not_().all()
    assert df["is_null"].dtype == pl.Boolean
    assert df["is_null"].null_count() == df.height


def test_u64_pair_to_uuid() -> None:
    def py_u64_pair_to_uuid(v: int) -> str:
        u = uuid.UUID(bytes=v.to_bytes(8, "big") + v.to_bytes(8, "big"))
        return str(u)

    df = pl.DataFrame(
        {"idx": list(range(1_000_000))}, schema={"idx": pl.UInt64}
    ).with_columns(
        uuid=u64_pair_to_uuid(high_bits="idx", low_bits="idx"),
        uuid_py=pl.col("idx").map_elements(py_u64_pair_to_uuid, return_dtype=pl.String),
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid_py"].null_count() == 0
    assert df["uuid_py"].dtype == pl.String
    assert_series_equal(df["uuid"], df["uuid_py"], check_names=False)
