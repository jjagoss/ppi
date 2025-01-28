from pydantic import BaseModel


class CommodityData(BaseModel):
    series_id: str
    year: int
    period: str
    value: float
    footnote_code: str
