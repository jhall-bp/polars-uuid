mod uuid_utils;
mod uuid_v4;
mod uuid_v7;
use pyo3::prelude::*;
use pyo3_polars::PolarsAllocator;

#[pymodule]
fn _internal(_py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

#[global_allocator]
static ALLOC: PolarsAllocator = PolarsAllocator::new();
