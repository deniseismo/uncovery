from dataclasses import dataclass


@dataclass
class AlbumInfo:
    title: str
    artist_name: str
    artist_names: list[str]
    names: list[str]
    rating: int
    spotify_id: str
    year: str
    image: str
    image_small: str = None
    image_medium: str = None
