from dataclasses import dataclass

from uncover.schemas.info_base import InfoBase


@dataclass
class AlbumInfo(InfoBase):
    title: str
    artist_name: str
    artist_names: list[str]
    names: list[str]
    rating: int
    image: str
    year: str = None
    image_small: str = None
    image_medium: str = None
    filtered_title: str = None
    id: int = 0
    spotify_name: str = None
    spotify_id: str = None

    def __repr__(self):
        return f"Album({self.title}) by Artist({self.artist_name}), {self.year}"
