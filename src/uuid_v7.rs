use std::fmt::Write;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::{ContextV7, Timestamp, Uuid};

// Kwarg Structs

#[derive(serde::Deserialize)]
struct Uuid7Kwargs {
    seconds_since_unix_epoch: f64,
}

impl Uuid7Kwargs {
    fn get_secs_and_subsec_nanosecs(&self) -> (u64, u32) {
        (
            self.seconds_since_unix_epoch.trunc() as u64,
            ((self.seconds_since_unix_epoch.fract()) * 1_000_000_000.0).round() as u32,
        )
    }
}

#[derive(serde::Deserialize)]
struct ExtractDatetimeKwargs {
    strict: bool,
}

// Random

#[polars_expr(output_type=String)]
fn uuid7_rand_now(inputs: &[Series]) -> PolarsResult<Series> {
    let ca = inputs[0].str()?;
    let out = ca.apply_into_string_amortized(|_value: &str, output: &mut String| {
        write!(output, "{}", Uuid::now_v7()).unwrap()
    });

    Ok(out.into_series())
}

#[polars_expr(output_type=String)]
fn uuid7_rand_now_single(_inputs: &[Series]) -> PolarsResult<Series> {
    let uuid = Uuid::now_v7();
    Ok(Series::new(
        PlSmallStr::from_static("uuid"),
        [uuid.to_string()],
    ))
}

#[polars_expr(output_type=String)]
fn uuid7_rand(inputs: &[Series], kwargs: Uuid7Kwargs) -> PolarsResult<Series> {
    let context = ContextV7::new();
    let (seconds, subsec_nanos) = kwargs.get_secs_and_subsec_nanosecs();

    let ca = inputs[0].str()?;
    let out = ca.apply_into_string_amortized(|_value: &str, output: &mut String| {
        let timestamp = Timestamp::from_unix(&context, seconds, subsec_nanos);
        write!(output, "{}", Uuid::new_v7(timestamp)).unwrap()
    });

    Ok(out.into_series())
}

#[polars_expr(output_type=String)]
fn uuid7_rand_single(_inputs: &[Series], kwargs: Uuid7Kwargs) -> PolarsResult<Series> {
    let (seconds, subsec_nanos) = kwargs.get_secs_and_subsec_nanosecs();
    let uuid = Uuid::new_v7(Timestamp::from_unix(uuid::NoContext, seconds, subsec_nanos));
    Ok(Series::new(
        PlSmallStr::from_static("uuid"),
        [uuid.to_string()],
    ))
}

// Extract timestamp

#[polars_expr(output_type_func=utc_millis_datetime_output)]
fn uuid7_extract_dt(inputs: &[Series], kwargs: ExtractDatetimeKwargs) -> PolarsResult<Series> {
    let ca: &StringChunked = inputs[0].str()?;

    let mut builder: PrimitiveChunkedBuilder<Int64Type> =
        PrimitiveChunkedBuilder::new(PlSmallStr::from_static("timestamp"), ca.len());

    if kwargs.strict {
        for opt_value in ca.into_iter() {
            if let Some(value) = opt_value {
                if let Some(timestamp) = parse_timestamp_from_uuid_string(value) {
                    builder.append_value(timestamp);
                } else {
                    polars_bail!(ComputeError: "Failed to extract timestamp from UUID string: {}", value);
                }
            } else {
                builder.append_null();
            }
        }
    } else {
        for opt_value in ca.into_iter() {
            let timestamp = opt_value.and_then(parse_timestamp_from_uuid_string);
            builder.append_option(timestamp);
        }
    }

    builder
        .finish()
        .into_series()
        .strict_cast(&DataType::Datetime(
            TimeUnit::Milliseconds,
            Some(TimeZone::UTC),
        ))
}

// Utils

/// Parse the milliseconds since the UNIX epoch encoded into a UUID string
fn parse_timestamp_from_uuid_string(uuid_string: &str) -> Option<i64> {
    Uuid::parse_str(uuid_string).ok().and_then(|x| {
        let (seconds, nanoseconds) = x.get_timestamp()?.to_unix();
        let secs_to_millisecs: i64 = seconds.checked_mul(1_000)?.try_into().ok()?;
        let nsecs_to_millisecs: i64 = (nanoseconds / 1_000_000).into();
        secs_to_millisecs.checked_add(nsecs_to_millisecs)
    })
}

// Necessary because we can't pass Datetime directly to the polars_expr macro. See https://github.com/pola-rs/pyo3-polars/issues/145
fn utc_millis_datetime_output(input_fields: &[Field]) -> PolarsResult<Field> {
    if input_fields.len() != 1 {
        polars_bail!(InvalidOperation: "Expected a single input field, found {}", input_fields.len());
    }

    Ok(Field::new(
        input_fields[0].name.clone(),
        DataType::Datetime(TimeUnit::Milliseconds, Some(TimeZone::UTC)),
    ))
}
