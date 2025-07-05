from __future__ import annotations

from pathlib import Path

import polars as pl
from polars.plugins import register_plugin_function

_LIB = Path(__file__).parent
_ARGS = (
    pl.repeat(
        pl.lit("", dtype=pl.String),
        n=pl.len(),
    )
)

_ARGS_SINGLE = (pl.lit("", dtype=pl.String),)

# Utils

def is_uuid(expr: str | pl.Expr) -> pl.Expr:
    """Returns a boolean `Series` indicating which values are valid UUID strings."""
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=(expr,),
        plugin_path=_LIB,
        function_name="is_uuid",
        is_elementwise=True,
    )

def u64_pair_to_uuid(*, high_bits: str | pl.Expr, low_bits: str | pl.Expr) -> pl.Expr:
    """Create a `Series` of UUID strings from two equal-length `Series` of 64bit values."""
    if isinstance(high_bits, str):
        high_bits = pl.col(high_bits)

    if isinstance(low_bits, str):
        low_bits = pl.col(low_bits)

    return register_plugin_function(
        args=(high_bits, low_bits),
        plugin_path=_LIB,
        function_name="u64_pair_to_uuid_string",
        is_elementwise=True,
    )

# UUIDv4

def uuid_v4() -> pl.Expr:
    """An expression that generates a series of random v4 UUIDs."""
    return register_plugin_function(
        args=_ARGS,
        plugin_path=_LIB,
        function_name="uuid4_rand",
        is_elementwise=True,
    )

def uuid_v4_single() -> pl.Expr:
    """An expression that generates a series repeating a single, random v4 UUID."""
    return register_plugin_function(
        args=_ARGS_SINGLE,
        plugin_path=_LIB,
        function_name="uuid4_rand",
        is_elementwise=True,
    )

# UUIDv7

def uuid_v7_now() -> pl.Expr:
    """An expression that generates a sorted series of random v7 UUIDs using the current time."""
    return register_plugin_function(
        args=_ARGS,
        plugin_path=_LIB,
        function_name="uuid7_rand_now",
        is_elementwise=True,
    )

def uuid_v7_now_single() -> pl.Expr:
    """An expression that generates a series with a single, random v7 UUID using the current time."""
    return register_plugin_function(
        args=_ARGS_SINGLE,
        plugin_path=_LIB,
        function_name="uuid7_rand_now",
        is_elementwise=True,
    )

def uuid_v7(*, timestamp: float) -> pl.Expr:
    """An expression that generates a sorted series of random v7 UUIDs using the given timestamp."""
    return register_plugin_function(
        args=_ARGS,
        plugin_path=_LIB,
        function_name="uuid7_rand",
        is_elementwise=True,
        kwargs={"seconds_since_unix_epoch": timestamp},
    )

def uuid_v7_single(*, timestamp: float) -> pl.Expr:
    """An expression that generates a series with a single, random v7 UUID using the given timestamp."""
    return register_plugin_function(
        args=_ARGS_SINGLE,
        plugin_path=_LIB,
        function_name="uuid7_rand",
        is_elementwise=True,
        kwargs={"seconds_since_unix_epoch": timestamp},
    )

def uuid_v7_extract_dt(expr: str | pl.Expr, /, *, strict: bool = True) -> pl.Expr:
    """Return a `Series` of UTC datetimes extracted from another `Series` of UUIDv7 strings."""
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=(expr,),
        plugin_path=_LIB,
        function_name="uuid7_extract_dt",
        is_elementwise=True,
        kwargs={"strict": strict}
    )
