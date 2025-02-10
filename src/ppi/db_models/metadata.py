import pandera as pa
from pandera import Column, Check

# Define the schema
Metadata = pa.DataFrameSchema({
    "series_id": Column(str),
    "group_code": Column(str),
    "item_code": Column(str),
    "seasonal": Column(str, Check.isin(["S", "U"])),  # Assuming 'S' and 'U' are the only valid values
    "base_date": Column(str, nullable=True),  # Allowing null values if base_date can be missing
    "series_title": Column(str),
    "begin_year": Column(int, Check.ge(1900)),  # Assuming the year should be >= 1900
    "begin_period": Column(str),
    "end_year": Column(int, Check.ge(1900)),
    "end_period": Column(str)
})
