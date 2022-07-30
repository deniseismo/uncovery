from dataclasses import dataclass, field

from uncover.schemas.info_base import InfoBase


@dataclass
class AlbumInfo(InfoBase):
    title: str
    artist_name: str
    artist_names: list[str]
    names: list[str]
    rating: int = None
    image: str = None
    image_small: str = None
    image_medium: str = None
    _image: str = field(init=False, repr=False, default=None)
    _image_small: str = field(init=False, repr=False, default=None)
    _image_medium: str = field(init=False, repr=False, default=None)
    filtered_title: str = None
    id: int = 0
    mbid: str = None
    spotify_name: str = None
    alternative_name: str = None
    spotify_id: str = None
    year: int = None

    @property
    def image(self) -> str:
        return self._image

    @image.setter
    def image(self, v: str) -> None:
        if type(v) is property:
            # initial value not specified, use default
            v = AlbumInfo._image
        if isinstance(v, str):
            v = self._remove_leading_slash(v)
        print(f"setting value= {v}")
        self._image = v

    @property
    def image_small(self) -> str:
        return self._image_small

    @image_small.setter
    def image_small(self, v: str) -> None:
        if type(v) is property:
            # initial value not specified, use default
            v = AlbumInfo._image_small
        if isinstance(v, str):
            v = self._remove_leading_slash(v)
        print(f"setting value= {v}")
        self._image_small = v

    @property
    def image_medium(self) -> str:
        return self._image_medium

    @image_medium.setter
    def image_medium(self, v: str) -> None:
        if type(v) is property:
            # initial value not specified, use default
            v = AlbumInfo._image_medium
        if isinstance(v, str):
            v = self._remove_leading_slash(v)
            self._image_medium = v

    @staticmethod
    def _remove_leading_slash(filename: str) -> str:
        """
        removes leading slashes "/" from the string
        :param filename: (str)
        :return: string with no "/" at the beginning
        """
        return filename.lstrip("/")

    def __repr__(self):
        album_description = f"Album({self.title}) by Artist({self.artist_name})"
        if self.year:
            album_description += f", {self.year}"
        return album_description

    def remove_duplicate_names(self):
        self.names = list(set(self.names))
        self.artist_names = list(set(self.artist_names))
