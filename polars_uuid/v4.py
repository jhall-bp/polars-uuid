from __future__ import annotations

import polars as pl
from polars.plugins import (
    register_plugin_function,
)
from polars_uuid._constants import PLUGIN_PATH, ARGS, ARGS_SINGLE


def uuid_v4(*, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 4 UUIDs.

    Returns:
        pl.Expr: A polars expression of random v4 UUIDs.

    Example:
        >>> df.with_columns(uuid=uuid_v4())
    """
    return register_plugin_function(
        args=ARGS_SINGLE if scalar else ARGS,
        plugin_path=PLUGIN_PATH,
        function_name="uuid4_rand",
        is_elementwise=not scalar,
        returns_scalar=scalar,
    )
