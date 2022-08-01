from dataclasses import dataclass
from datetime import datetime
from typing import NamedTuple, Optional

from tekore._model import SimpleAlbum, FullArtist

from uncover.schemas.info_base import InfoBase


class TimeSpan(NamedTuple):
    """
    represents time span picked by user (e.g. in explore mode) [start_date, end_date]

    :attr start_date: (datetime) year from
    :attr end_date: (datetime) year to (incl.)
    """
    start_date: datetime
    end_date: datetime

    def __repr__(self):
        return f"({self.start_date.year} — {self.end_date.year})"


class CollageDimensions(NamedTuple):
    """
    represents collage dimensions in pixels (int)

    :attr width: (int) width in pixels
    :attr height: (int) height in pixels
    """
    width: int
    height: int

    def __repr__(self):
        return f"{self.width} x {self.height}"


class AlbumMatch(NamedTuple):
    """
    stores album (SimpleAlbum from Spotify) and the ratio (int, percent)
    showing how close particular album to the one user's searching for

    :attr album: (SimpleAlbum) album in question
    :attr ratio: (int) shows how close album is to the other one (100 — perfect score)
    """
    album: SimpleAlbum
    ratio: int


class ArtistMatch(NamedTuple):
    """
    stores artist (FullArtist from Spotify) and the ratio (int, percent)
    showing how close particular artist to the one user's searching for

    :attr artist: (FullArtist) artist in question
    :attr ratio: (int) shows how close artist is to the other one (100 — perfect score)
    """
    artist: FullArtist
    ratio: int


class ImageOffset(NamedTuple):
    """
    stores (x, y) offset params

    :attr x: (int) offset (horizontally) in pixels
    :attr y: (int) offset (vertically) in pixels
    """
    x: int
    y: int

    def __repr__(self):
        return f"({self.x}, {self.y})"


class ImageSize(NamedTuple):
    """
    stores image size

    :attr width: (int) width in pixels
    :attr height: (int) height in pixels
    """
    width: int
    height: int

    def __repr__(self):
        return f"{self.width} x {self.height}"


@dataclass
class SpotifyAlbumSearchParams(InfoBase):
    """
    spotify search params used in spotify request (usually through tekore spotify library)

    :attr query: (str) what we're searching for
    :attr types: (tuple[str]) type of media/request (album, artist, etc.)
    :attr market: (Optional[str]) 2-letter country code (market on Spotify)
    :attr limit: (int) limits amount of search results
    """
    query: str
    types: tuple[str]
    market: Optional[str] = None
    limit: int = 50
