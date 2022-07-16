from datetime import datetime
from typing import NamedTuple


class TimeSpan(NamedTuple):
    start_date: datetime
    end_date: datetime


class CollageDimensions(NamedTuple):
    width: int
    height: int
