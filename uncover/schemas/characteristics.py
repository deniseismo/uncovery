from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional

from tekore._model import SimpleAlbum

from uncover.schemas.info_base import InfoBase


class TimeSpan(NamedTuple):
    start_date: datetime
    end_date: datetime


class CollageDimensions(NamedTuple):
    width: int
    height: int


class AlbumMatch(NamedTuple):
    album: SimpleAlbum
    ratio: int


@dataclass
class SpotifyAlbumSearchParams(InfoBase):
    query: str
    types: tuple[str]
    market: Optional[str] = None
    limit: int = 50


