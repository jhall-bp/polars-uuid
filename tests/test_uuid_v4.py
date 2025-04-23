import polars as pl

from polars_uuid import uuid_v4

UUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"

def test_uuid_v4():
    df = (
        pl.DataFrame({ "idx": list(range(10_000_000)) })
        .with_columns(uuid=uuid_v4())
    )

    assert df["uuid"].null_count() == 0
    assert df["uuid"].dtype == pl.String
    assert df["uuid"].is_unique().all()
    assert (df["uuid"].str.count_matches(UUID_PATTERN) == 1).all()
