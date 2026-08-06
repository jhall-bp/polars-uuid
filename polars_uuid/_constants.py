from __future__ import annotations

from pathlib import Path
import polars as pl


PLUGIN_PATH = Path(__file__).parent.joinpath("_internal.abi3.so").resolve(strict=True)

ARGS = pl.first()
ARGS_SINGLE = pl.lit(None, dtype=pl.Null)
