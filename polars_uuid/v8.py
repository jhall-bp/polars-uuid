from __future__ import annotations

from typing import overload

import polars as pl
from polars.plugins import (
    register_plugin_function,
)
from polars_uuid._constants import PLUGIN_PATH, ARGS, ARGS_SINGLE


def uuid_v8_from_bytes(expr: str | pl.Expr, /) -> pl.Expr:
    """
    Generates version 8 UUIDs from binary values.

    Parameters:
        expr (str | pl.Expr): The input column name or polars expression containing
            binary values. Values shorter than 16 bytes are zero-padded, and values
            longer than 16 bytes are truncated.

    Returns:
        pl.Expr: A polars expression of UUIDv8 strings generated from the input bytes.

    Example:
        >>> df.with_columns(uuid=uuid_v8_from_bytes("payload"))
    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=PLUGIN_PATH,
        function_name="uuid8_from_binary",
        is_elementwise=True,
    )


def uuid_v8_by_hashing_str(expr: str | pl.Expr, /) -> pl.Expr:
    """
    Generates deterministic version 8 UUIDs by hashing string values using BLAKE3.

    Parameters:
        expr (str | pl.Expr): The input column name or polars expression containing
            string values to hash.

    Returns:
        pl.Expr: A polars expression of UUIDv8 strings generated from BLAKE3 hashes
            of the input strings.

    Example:
        >>> df.with_columns(uuid=uuid_v8_by_hashing_str("name"))
    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=PLUGIN_PATH,
        function_name="uuid8_by_hashing_string",
        is_elementwise=True,
    )
