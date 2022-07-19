from dataclasses import dataclass

from uncover.schemas.album_schema import AlbumInfo
from uncover.schemas.info_base import InfoBase


@dataclass
class ResponseInfo(InfoBase):
    type: str
    query: str = None


@dataclass
class AlbumCoversResponse(InfoBase):
    info: ResponseInfo
    albums: list[AlbumInfo]
