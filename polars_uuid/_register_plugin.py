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

def uuid_v4() -> pl.Expr:
    """An expression that generates a series of random UUIDs."""
    return register_plugin_function(
        args=_ARGS,
        plugin_path=_LIB,
        function_name="uuid4_rand",
        is_elementwise=True,
    )

def uuid_v4_single() -> pl.Expr:
    """An expression that generates a series with a single, random UUID."""
    return register_plugin_function(
        args=_ARGS_SINGLE,
        plugin_path=_LIB,
        function_name="uuid4_rand",
        is_elementwise=True,
    )
