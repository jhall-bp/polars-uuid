use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

#[polars_expr(output_type=String)]
fn uuid4_rand(inputs: &[Series]) -> PolarsResult<Series> {
    let mut buffer = Uuid::encode_buffer();
    let height = inputs[0].len();
    let mut builder = StringChunkedBuilder::new(PlSmallStr::from_static("uuid"), height);
    for _ in 0..height {
        builder.append_value(Uuid::new_v4().hyphenated().encode_lower(&mut buffer));
    }
    Ok(builder.finish().into_series())
}
