from __future__ import annotations

from pathlib import Path

import polars as pl

PLUGIN_PATH = Path(__file__).parent.joinpath("_internal.abi3.so").resolve(strict=True)

ARGS = pl.first()
# A one-element input tied to the current frame/group prevents literal hoisting.
# The generators use its length, not the count it contains.
ARGS_SINGLE = pl.len()
