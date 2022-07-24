from dataclasses import dataclass
from datetime import datetime

from uncover.schemas.info_base import InfoBase


@dataclass
class AlbumInfo(InfoBase):
    title: str
    artist_name: str
    artist_names: list[str]
    names: list[str]
    rating: int
    image: str = None
    image_small: str = None
    image_medium: str = None
    filtered_title: str = None
    id: int = 0
    mbid: str = None
    spotify_name: str = None
    alternative_name: str = None
    spotify_id: str = None
    release_date: datetime = None

    def __repr__(self):
        album_description = f"Album({self.title}) by Artist({self.artist_name})"
        if self.release_date:
            album_description += f", {self.release_date.year}"
        return album_description

    def remove_duplicate_names(self):
        self.names = list(set(self.names))
        self.artist_names = list(set(self.artist_names))
