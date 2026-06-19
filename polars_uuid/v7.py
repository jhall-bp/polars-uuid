from __future__ import annotations

from typing import overload

import polars as pl
from polars.plugins import (
    register_plugin_function,
)
from polars_uuid._constants import PLUGIN_PATH, ARGS, ARGS_SINGLE


def uuid_v7_now(*, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the current system time.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs.

    Notes:
        - This expression uses uuid::Uuid::now_v7(). This means the generated
            UUIDs will be ordered, but may not all have the same timestamp.

    Example:
        >>> df.with_columns(uuid=uuid_v7_now())
    """
    return register_plugin_function(
        args=ARGS_SINGLE if scalar else ARGS,
        plugin_path=PLUGIN_PATH,
        function_name="uuid7_rand_now",
        is_elementwise=not scalar,
        returns_scalar=scalar,
    )


@overload
def uuid_v7(*, timestamp: int | float, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the given timestamp.

    Parameters:
        timestamp (int | float | str | pl.Expr): The timestamp to use when generating UUIDs in seconds since the UNIX epoch.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs based on the given timestamp.

    Notes:
        - UUIDs sort by timestamp at millisecond precision, but UUIDs generated with
          equal millisecond timestamps are randomly ordered rather than input ordered.

    Example:
        >>> dt = datetime.datetime(2000, 1, 1, tz=datetime.UTC)
        >>> df.with_columns(uuid=uuid_v7(timestamp=dt.timestamp()))
    """


@overload
def uuid_v7(*, timestamp: str | pl.Expr) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the given timestamp values.

    Parameters:
        timestamp (str | pl.Expr): The timestamp to use when generating UUIDs in seconds since the UNIX epoch. String values are treated as column names.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs based on the given timestamp.

    Notes:
        - UUIDs sort by timestamp at millisecond precision, but UUIDs generated with
          equal millisecond timestamps are randomly ordered rather than input ordered.

    Example:
        >>> dt = datetime.datetime(2000, 1, 1, tz=datetime.UTC)
        >>> df.with_columns(uuid=uuid_v7(timestamp=pl.col("created_at")))
    """


def uuid_v7(*, timestamp: int | float | str | pl.Expr, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the given timestamp.

    Parameters:
        timestamp (float | str | pl.Expr): The timestamp to use when generating UUIDs in seconds since the UNIX epoch. Float values are treated as literals and string values are treated as column names.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs based on the given timestamp.

    Notes:
        - UUIDs sort by timestamp at millisecond precision, but UUIDs generated with
          equal millisecond timestamps are randomly ordered rather than input ordered.

    Example:
        >>> dt = datetime.datetime(2000, 1, 1, tz=datetime.UTC)
        >>> df.with_columns(uuid=uuid_v7(timestamp=dt.timestamp()))
    """
    if isinstance(timestamp, (float, int)):
        kwargs: dict[str, object] = {"seconds_since_unix_epoch": timestamp}
        fn_name = "uuid7_rand"
        args = (ARGS_SINGLE if scalar else ARGS,)
    else:
        args = pl.col(timestamp) if isinstance(timestamp, str) else timestamp
        kwargs: dict[str, object] = {}
        fn_name = "uuid7_rand_dynamic"

    return register_plugin_function(
        args=args,
        plugin_path=PLUGIN_PATH,
        function_name=fn_name,
        is_elementwise=not scalar,
        returns_scalar=scalar,
        kwargs=kwargs,
    )


def uuid_v7_extract_dt(expr: str | pl.Expr, /, *, strict: bool = True) -> pl.Expr:
    """
    Extract UTC datetimes from UUIDv7 strings.

    Parameters:
        expr (str | pl.Expr): The input column name or polars expression containing UUIDv7 strings.
        strict (bool, optional): If `True`, raises an error on invalid UUIDv7 strings. If `False`, returns null for invalid entries.

    Returns:
        pl.Expr: A polars expression yielding a Series of UTC datetimes extracted from the UUIDv7 strings.

    Notes:
        - UUIDv7 timestamps have millisecond precision

    Examples:
        >>> df.with_columns(
        >>>     dt=uuid_v7_extract_dt(pl.col("uuid"), strict=False)
        >>> )

    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=PLUGIN_PATH,
        function_name="uuid7_extract_dt",
        is_elementwise=True,
        kwargs={"strict": strict},
    )
