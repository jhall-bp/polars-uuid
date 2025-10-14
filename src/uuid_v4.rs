use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

#[polars_expr(output_type=String)]
fn uuid4_rand(inputs: &[Series]) -> PolarsResult<Series> {
    let height = inputs[0].len();
    let mut builder = StringChunkedBuilder::new(PlSmallStr::from_static("uuid"), height);
    for _ in 0..height {
        builder.append_value(Uuid::new_v4().to_string());
    }
    Ok(builder.finish().into_series())
}

#[polars_expr(output_type=String)]
fn uuid4_rand_single(_inputs: &[Series]) -> PolarsResult<Series> {
    let uuid = Uuid::new_v4();
    Ok(Series::new(
        PlSmallStr::from_static("uuid"),
        [uuid.to_string()],
    ))
}
