from dataclasses import dataclass

from uncover.schemas.info_base import InfoBase


@dataclass
class AlbumInfo(InfoBase):
    """
    stores all the information about album, album covers, album artists, etc. that will be sent to the user

    :attr title: (str) album's title
    :attr artist_name: (str) artist's name
    :attr artist_names: (list[str]) a list of possible artist names
        (the way it can be written, e.g. with or without the The, alternative artist's name);
        the list is used in the guessing game to make it easier & more flexible
    :attr names: (list[str]) a list of possible album titles
        (the way it can be written, e.g. with or without the The,
        alternative album's title (e.g. The White Album));
        the list is used in the guessing game to make it easier & more flexible
    :attr rating: (int) album's rating (as per lastfm or (in some cases) spotify)
    :attr image: (str) album's cover image (url), default size
    :attr image_small: (str) album's cover image (url), small size
    :attr image_medium: (str) album's cover image (url), medium size
    :attr filtered_title: (str) filtered album's title
        (after getting rid of unnecessary/annoying tags that can be found on spotify or elsewhere
        (e.g. ... 2002 Anniversary version, (Studio), Single Version, etc.))
    :attr id: (int) album's (order) number in a list of returned albums
    :attr mbid: (str) musicbrainz id for the album
    :attr spotify_name: (str) album name on Spotify (in some cases it can differ from the official one)
    :attr alternative_name: (str) alternative album's title (e.g. The White Album, Cross, etc.)
    :attr spotify_id: (str) album's spotify id
    :attr year: (int) release date
    """
    title: str
    artist_name: str
    artist_names: list[str]
    names: list[str]
    rating: int = None
    image: str = None
    image_small: str = None
    image_medium: str = None
    filtered_title: str = None
    id: int = 0
    mbid: str = None
    spotify_name: str = None
    alternative_name: str = None
    spotify_id: str = None
    year: int = None

    def __repr__(self):
        album_description = f"Album({self.title}) by Artist({self.artist_name})"
        if self.year:
            album_description += f", {self.year}"
        return album_description

    def remove_duplicate_names(self):
        """
        removes duplicate album titles from the list of names & duplicate artist name from the list of artist names
        """
        self.names = list(set(self.names))
        self.artist_names = list(set(self.artist_names))
