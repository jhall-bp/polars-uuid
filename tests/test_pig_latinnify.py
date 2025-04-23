import polars as pl

from polars_uuid import uuid_v4


def test_piglatinnify():
    df = pl.DataFrame(
        {
            "english": ["this", "is", "not", "pig", "latin"],
        }
    )
    result = df.with_columns(pig_latin=uuid_v4())

    expected_df = pl.DataFrame(
        {
            "english": ["this", "is", "not", "pig", "latin"],
            "pig_latin": ["histay", "siay", "otnay", "igpay", "atinlay"],
        }
    )

    assert result.equals(expected_df)
