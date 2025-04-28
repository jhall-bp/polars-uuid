#![allow(clippy::unused_unit)]
use std::fmt::Write;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::{Timestamp, Uuid, ContextV7};

#[derive(serde::Deserialize)]
struct Uuid7Kwargs {
    seconds_since_unix_epoch: f64,
}

#[polars_expr(output_type=String)]
fn uuid7_rand_now(inputs: &[Series]) -> PolarsResult<Series> {
    let ca = inputs[0].str()?;
    let out = ca.apply_into_string_amortized(|_value: &str, output: &mut String| {
        write!(output, "{}", Uuid::now_v7()).unwrap()
    });

    Ok(out.into_series())
}

#[polars_expr(output_type=String)]
fn uuid7_rand(inputs: &[Series], kwargs: Uuid7Kwargs) -> PolarsResult<Series> {
    let context = ContextV7::new();
    let seconds = kwargs.seconds_since_unix_epoch.trunc() as u64;
    let subsec_nanos = ((kwargs.seconds_since_unix_epoch.fract()) * 1_000_000_000.0).round() as u32;

    let ca = inputs[0].str()?;
    let out = ca.apply_into_string_amortized(|_value: &str, output: &mut String| {
        let timestamp = Timestamp::from_unix(&context, seconds, subsec_nanos);
        write!(output, "{}", Uuid::new_v7(timestamp)).unwrap()
    });

    Ok(out.into_series())
}
