use std::fmt::Write;

use polars::prelude::{arity::binary_elementwise_into_string_amortized, *};
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

#[polars_expr(output_type=Boolean)]
fn is_uuid(inputs: &[Series]) -> PolarsResult<Series> {
    let ca: &StringChunked = inputs[0].str()?;
    let out: BooleanChunked =
        ca.apply_nonnull_values_generic(DataType::Boolean, |x| Uuid::parse_str(x).is_ok());
    Ok(out
        .into_series()
        .with_name(PlSmallStr::from_static("is_uuid")))
}

#[polars_expr(output_type=String)]
fn u128_to_uuid_string(inputs: &[Series]) -> PolarsResult<Series> {
    let values = inputs[0].u128()?;
    let mut buffer = Uuid::encode_buffer();

    let out = values.apply_into_string_amortized(|value, out| {
        let uuid = Uuid::from_u128(value);
        let uuid_str = uuid.as_hyphenated().encode_lower(&mut buffer);
        out.write_str(uuid_str).unwrap();
    });

    Ok(out.into_series().with_name(PlSmallStr::from_static("uuid")))
}

#[polars_expr(output_type=String)]
fn u64_pair_to_uuid_string(inputs: &[Series]) -> PolarsResult<Series> {
    let ca_hi_bits = inputs[0].u64()?;
    let ca_lo_bits = inputs[1].u64()?;
    let mut buffer = Uuid::encode_buffer();

    let out = binary_elementwise_into_string_amortized(
        ca_hi_bits,
        ca_lo_bits,
        |hi_bits, lo_bits, output| {
            let uuid = Uuid::from_u64_pair(hi_bits, lo_bits);
            output.write_str(uuid.as_hyphenated().encode_lower(&mut buffer)).unwrap()
        },
    );

    Ok(out.into_series().with_name(PlSmallStr::from_static("uuid")))
}
