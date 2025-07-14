import uuid

import polars as pl
from polars.testing import assert_series_equal
import hypothesis.strategies as st
from hypothesis import given
from polars_uuid import is_uuid, u64_pair_to_uuid, uuid_v4
from polars.testing.parametric import column, dataframes


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


@given(
    dataframes(
        cols=[
            column(
                "hi_bits",
                dtype=pl.UInt64,
                strategy=st.integers(min_value=0, max_value=(1 << 64) - 1),
            ),
            column(
                "lo_bits",
                dtype=pl.UInt64,
                strategy=st.integers(min_value=0, max_value=(1 << 64) - 1),
            ),
        ],
        min_size=5,
        lazy=True,
    )
)
def test_u64_pair_to_uuid(lf: pl.LazyFrame) -> None:
    def py_u64_pair_to_uuid(pair: dict[str, int]) -> str:
        hi = pair["hi_bits"]
        lo = pair["lo_bits"]
        u = uuid.UUID(bytes=hi.to_bytes(8, "big") + lo.to_bytes(8, "big"))
        return str(u)

    df = lf.with_columns(
        uuid=u64_pair_to_uuid(high_bits="hi_bits", low_bits="lo_bits"),
        uuid_py=pl.struct(hi_bits="hi_bits", lo_bits="lo_bits").map_elements(
            py_u64_pair_to_uuid, return_dtype=pl.String
        ),
    ).collect()

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid_py"].null_count() == 0
    assert df["uuid_py"].dtype == pl.String
    assert_series_equal(df["uuid"], df["uuid_py"], check_names=False)
