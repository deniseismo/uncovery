from dataclasses import dataclass

from uncover.schemas.album_schema import AlbumInfo
from uncover.schemas.info_base import InfoBase


@dataclass
class ResponseInfo(InfoBase):
    """
    dataclass used to represent additional information for user's request

    :attr type: (str) type of request (e.g. artist, playlist, explore, etc.)
    :attr query: (str) (usually) the request itself (e.g. artist's name, username on lastfm, etc.)
    """
    type: str
    query: str = None


@dataclass
class AlbumCoversResponse(InfoBase):
    """
    dataclass used to represent main response that will be returned to the user

    :attr info: (ResponseInfo) additional information for user's request
    :attr albums: (list[AlbumInfo) all the information about albums & album covers returned to the user
    """
    info: ResponseInfo
    albums: list[AlbumInfo]
