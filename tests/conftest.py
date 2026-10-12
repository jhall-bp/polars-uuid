from collections.abc import Iterator
from typing import TYPE_CHECKING

import polars as pl
import pytest

if TYPE_CHECKING:
    from polars._typing import EngineType


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POLARS_VERBOSE", "1")


@pytest.fixture(params=["auto", "in-memory", "streaming"])
def engine(request: pytest.FixtureRequest) -> Iterator[EngineType]:
    # Exercise batch boundaries even with a single Polars worker.
    with pl.Config(set_streaming_chunk_size=128):
        yield request.param
