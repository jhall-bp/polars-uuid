use std::fmt::Write;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::{ClockSequence, NoContext, Timestamp, Uuid};

const UUID_V7_MAX_TIMESTAMP_MILLIS: u64 = (1_u64 << 48) - 1;

// Kwarg Structs

#[derive(serde::Deserialize)]
struct Uuid7Kwargs {
    seconds_since_unix_epoch: f64,
}

impl Uuid7Kwargs {
    fn get_unix_timestamp_millis(&self) -> PolarsResult<u64> {
        unix_timestamp_seconds_to_millis(self.seconds_since_unix_epoch)
    }
}

#[derive(serde::Deserialize)]
struct ExtractDatetimeKwargs {
    strict: bool,
}

// Random

#[polars_expr(output_type=String)]
fn uuid7_rand_dynamic(inputs: &[Series]) -> PolarsResult<Series> {
    let datetimes = inputs[0]
        .datetime()?
        .cast_time_unit(TimeUnit::Milliseconds)
        .into_physical();
    let mut buffer = Uuid::encode_buffer();

    let out: StringChunked =
        datetimes.try_apply_into_string_amortized(|timestamp_ms: i64, output: &mut String| {
            let timestamp_ms = unix_timestamp_millis_from_i64(timestamp_ms)?;
            let uuid_v7 = uuid_v7_from_unix_millis(&NoContext, timestamp_ms);
            output
                .write_str(uuid_v7.as_hyphenated().encode_lower(&mut buffer))
                .unwrap();
            Ok::<(), PolarsError>(())
        })?;

    Ok(out.into_series().with_name(PlSmallStr::from_static("uuid")))
}

#[polars_expr(output_type=String)]
fn uuid7_rand_now(inputs: &[Series]) -> PolarsResult<Series> {
    let mut buffer = Uuid::encode_buffer();
    let height = inputs[0].len();
    let mut builder = StringChunkedBuilder::new(PlSmallStr::from_static("uuid"), height);
    for _ in 0..height {
        builder.append_value(Uuid::now_v7().hyphenated().encode_lower(&mut buffer));
    }
    let mut series = builder.finish().into_series();
    series.set_sorted_flag(polars::series::IsSorted::Ascending);
    Ok(series)
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
    let timestamp_ms = kwargs.get_unix_timestamp_millis()?;

    let mut buffer = Uuid::encode_buffer();
    let height = inputs[0].len();
    let mut builder = StringChunkedBuilder::new(PlSmallStr::from_static("uuid"), height);
    for _ in 0..height {
        builder.append_value(
            uuid_v7_from_unix_millis(&NoContext, timestamp_ms)
                .hyphenated()
                .encode_lower(&mut buffer),
        );
    }
    Ok(builder.finish().into_series())
}

#[polars_expr(output_type=String)]
fn uuid7_rand_single(_inputs: &[Series], kwargs: Uuid7Kwargs) -> PolarsResult<Series> {
    let timestamp_ms = kwargs.get_unix_timestamp_millis()?;
    let uuid = uuid_v7_from_unix_millis(&uuid::NoContext, timestamp_ms);
    Ok(Series::new(
        PlSmallStr::from_static("uuid"),
        [uuid.to_string()],
    ))
}

// Extract timestamp

#[polars_expr(output_type_func=utc_millis_datetime_output)]
fn uuid7_extract_dt(inputs: &[Series], kwargs: ExtractDatetimeKwargs) -> PolarsResult<Series> {
    let ca = inputs[0].str()?;

    let mut builder: PrimitiveChunkedBuilder<Int64Type> =
        PrimitiveChunkedBuilder::new(PlSmallStr::from_static("timestamp"), ca.len());

    if kwargs.strict {
        for opt_value in ca.iter() {
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
        for opt_value in ca.iter() {
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

fn unix_timestamp_seconds_to_millis(seconds_since_unix_epoch: f64) -> PolarsResult<u64> {
    if !seconds_since_unix_epoch.is_finite() {
        polars_bail!(ComputeError: "UUIDv7 timestamp must be finite");
    }

    if seconds_since_unix_epoch < 0.0 {
        polars_bail!(ComputeError: "UUIDv7 timestamp must be at or after the UNIX epoch");
    }

    let timestamp_ms = (seconds_since_unix_epoch * 1_000.0).floor();
    if timestamp_ms > UUID_V7_MAX_TIMESTAMP_MILLIS as f64 {
        polars_bail!(
            ComputeError:
            "UUIDv7 timestamp exceeds the maximum 48-bit millisecond value"
        );
    }

    Ok(timestamp_ms as u64)
}

fn unix_timestamp_millis_from_i64(timestamp_ms: i64) -> PolarsResult<u64> {
    let timestamp_ms = u64::try_from(timestamp_ms).map_err(
        |_| polars_err!(ComputeError: "UUIDv7 timestamp must be at or after the UNIX epoch"),
    )?;

    if timestamp_ms > UUID_V7_MAX_TIMESTAMP_MILLIS {
        polars_bail!(
            ComputeError:
            "UUIDv7 timestamp exceeds the maximum 48-bit millisecond value"
        );
    }

    Ok(timestamp_ms)
}

fn uuid_v7_from_unix_millis<C: ClockSequence<Output = impl Into<u128>>>(
    context: &C,
    timestamp_ms: u64,
) -> Uuid {
    let seconds = timestamp_ms / 1_000;
    let subsec_nanos = ((timestamp_ms % 1_000) * 1_000_000) as u32;
    Uuid::new_v7(Timestamp::from_unix(context, seconds, subsec_nanos))
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
