from pydantic import BaseModel
class Metadata(BaseModel):

    series_id: str
    group_code: str
    item_code: str
    seasonal: str
    base_data: str
    begin_year: int
    begin_period: str
    end_year: int
    end_period: str
