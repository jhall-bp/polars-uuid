import time

import fastuuid
import polars as pl

from polars_uuid import uuid_v4

df = pl.DataFrame(
    {
        "english": [i for i in range(10_000_000)],
    }
)

start = time.time()
result = df.with_columns(id=uuid_v4())
end = time.time()
# print(result)
print(f"time: {end - start}s")

# start = time.time()
# result = df.with_columns(pl.Series("id", fastuuid.uuid4_as_strings_bulk(df.height)))
# end = time.time()
# # print(result)
# print(f"time: {end - start}s")


start = time.time()
result = df.with_columns(pl.when(pl.col("english") % 2 == 0).then(uuid_v4()).otherwise("english"))
end = time.time()
print(result)
print(f"time: {end - start}s")