use std::fmt::Write;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

// Random

#[polars_expr(output_type=String)]
fn uuid8_from_binary(inputs: &[Series]) -> PolarsResult<Series> {
    let values = inputs[0].binary()?;
    let mut buffer = Uuid::encode_buffer();

    let out: StringChunked =
        values.apply_into_string_amortized(|bytes: &[u8], output: &mut String| {
            let n = bytes.len().min(16);
            let mut bytes_truncated = [0u8; 16];
            bytes_truncated[..n].copy_from_slice(&bytes[..n]);

            let uuid = Uuid::new_v8(bytes_truncated);
            output
                .write_str(uuid.as_hyphenated().encode_lower(&mut buffer))
                .unwrap();
        });

    Ok(out.into_series().with_name(PlSmallStr::from_static("uuid")))
}

#[polars_expr(output_type=String)]
fn uuid8_by_hashing_string(inputs: &[Series]) -> PolarsResult<Series> {
    let values = inputs[0].str()?;
    let mut buffer = Uuid::encode_buffer();

    let out: StringChunked =
        values.apply_into_string_amortized(|value: &str, output: &mut String| {
            let hash = blake3::hash(value.as_bytes());
            let mut uuid_bytes = [0u8; 16];
            uuid_bytes.copy_from_slice(&hash.as_bytes()[..16]);
            let uuid = Uuid::new_v8(uuid_bytes);
            output
                .write_str(uuid.as_hyphenated().encode_lower(&mut buffer))
                .unwrap();
        });

    Ok(out.into_series().with_name(PlSmallStr::from_static("uuid")))
}
