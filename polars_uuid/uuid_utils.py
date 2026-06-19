from __future__ import annotations

from typing import overload

import polars as pl
from polars.plugins import (
    register_plugin_function,
)
from polars_uuid._constants import PLUGIN_PATH, ARGS, ARGS_SINGLE


def is_uuid(expr: str | pl.Expr) -> pl.Expr:
    """
    Check if values in a column or expression are valid UUID strings.

    Parameters
    ----------
    expr : str or pl.Expr
        The name of the column (as a string) or a polars expression to check for valid UUID strings.

    Returns
    -------
    pl.Expr
        A boolean polars expression indicating which values are valid UUID strings.

    Examples
    --------
    >>> df = pl.DataFrame({"id": ["550e8400-e29b-41d4-a716-446655440000", "not-a-uuid"]})
    >>> df.with_columns(is_uuid("id").alias("is_valid_uuid"))
    shape: (2, 2)
    ┌──────────────────────────────────────┬───────────────┐
    │ id                                   ┆ is_valid_uuid │
    │ ---                                  ┆ ---           │
    │ str                                  ┆ bool          │
    ╞══════════════════════════════════════╪═══════════════╡
    │ 550e8400-e29b-41d4-a716-446655440000 ┆ true          │
    │ not-a-uuid                           ┆ false         │
    └──────────────────────────────────────┴───────────────┘
    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=PLUGIN_PATH,
        function_name="is_uuid",
        is_elementwise=True,
    )


def u128_to_uuid(values: str | pl.Expr, /) -> pl.Expr:
    """
    Converts u128 integers into UUID strings.

    Parameters:
        values (str | pl.Expr): The column name or polars expression representing the u128 values.

    Returns:
        pl.Expr: A polars expression that produces a `Series` of UUID strings.

    Notes:
        - The resulting strings may not be valid UUIDs according to RFC 4122 / RFC 9562.
    """
    if isinstance(values, str):
        values = pl.col(values)

    return register_plugin_function(
        args=values,
        plugin_path=PLUGIN_PATH,
        function_name="u128_to_uuid_string",
        is_elementwise=True,
    )


def u64_pair_to_uuid(*, high_bits: str | pl.Expr, low_bits: str | pl.Expr) -> pl.Expr:
    """
    Converts two 64-bit integers into UUID strings.

    Parameters:
        high_bits (str | pl.Expr): The column name or polars expression representing the high 64 bits of the UUID.
        low_bits (str | pl.Expr): The column name or polars expression representing the low 64 bits of the UUID.

    Returns:
        pl.Expr: A polars expression that produces a `Series` of UUID strings.

    Notes:
        - Both `high_bits` and `low_bits` must refer to columns or expressions of equal length.
        - The resulting strings may not be valid UUIDs according to RFC 4122 / RFC 9562.
    """
    if isinstance(high_bits, str):
        high_bits = pl.col(high_bits)

    if isinstance(low_bits, str):
        low_bits = pl.col(low_bits)

    return register_plugin_function(
        args=(high_bits, low_bits),
        plugin_path=PLUGIN_PATH,
        function_name="u64_pair_to_uuid_string",
        is_elementwise=True,
    )
