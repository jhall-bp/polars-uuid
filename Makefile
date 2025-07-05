SHELL=/bin/bash

venv:
	uv sync --group dev

install:
	unset CONDA_PREFIX && \
	uv run maturin develop

install-release:
	unset CONDA_PREFIX && \
	uv run maturin develop --release

pre-commit:
	rustup component add rustfmt && rustup component add clippy
	cargo fmt --all && cargo clippy --all-features
	uv run ruff check . --fix --exit-non-zero-on-fix
	uv run ruff format polars_uuid tests

test:
	uv run pytest tests
