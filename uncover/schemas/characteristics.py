from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional

from tekore._model import SimpleAlbum

from uncover.schemas.info_base import InfoBase


class TimeSpan(NamedTuple):
    start_date: datetime
    end_date: datetime

    def __repr__(self):
        return f"({self.start_date.year} — {self.end_date.year})"


class CollageDimensions(NamedTuple):
    width: int
    height: int


class AlbumMatch(NamedTuple):
    album: SimpleAlbum
    ratio: int


class ImageOffset(NamedTuple):
    x: int
    y: int


class ImageSize(NamedTuple):
    width: int
    height: int


@dataclass
class SpotifyAlbumSearchParams(InfoBase):
    query: str
    types: tuple[str]
    market: Optional[str] = None
    limit: int = 50


