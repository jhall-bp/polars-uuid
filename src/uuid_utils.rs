use std::iter::zip;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

#[polars_expr(output_type=Boolean)]
fn is_uuid(inputs: &[Series]) -> PolarsResult<Series> {
    let ca: &StringChunked = inputs[0].str()?;
    let out: BooleanChunked =
        ca.apply_nonnull_values_generic(DataType::Boolean, |x| Uuid::parse_str(x).is_ok());
    Ok(out.into_series())
}

#[polars_expr(output_type=String)]
fn u64_pair_to_uuid_string(inputs: &[Series]) -> PolarsResult<Series> {
    let ca1 = inputs[0].u64()?;
    let ca2 = inputs[1].u64()?;

    if ca1.len() != ca2.len() {
        polars_bail!(ShapeMismatch: "Both inputs must have the same length; found {} and {}", ca1.len(), ca2.len());
    }

    let mut builder = StringChunkedBuilder::new(PlSmallStr::from_static("uuid"), ca1.len());

    for opt_values in zip(ca1.into_iter(), ca2.into_iter()) {
        match opt_values {
            (Some(high), Some(low)) => {
                let uuid = Uuid::from_u64_pair(high, low);
                builder.append_value(uuid.to_string());
            },
            _ => builder.append_null(),
        }
    }

    Ok(builder.finish().into_series())
}
