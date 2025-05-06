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
