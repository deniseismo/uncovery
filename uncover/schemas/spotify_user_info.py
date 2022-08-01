from dataclasses import dataclass
from typing import Optional

from uncover.schemas.info_base import InfoBase


@dataclass
class SpotifyUserAuth(InfoBase):
    """
    dataclass used to store Spotify user authentication params

    :attr spotify_user_id: (str) spotify user id (unique id on Spotify)
    :attr token: (str) access token
    """
    spotify_user_id: Optional[str] = None
    token: Optional[str] = None


@dataclass
class SpotifyUserProfile(InfoBase):
    """
    dataclass used to store information about Spotify User

    :attr username: (str) spotify username
    :attr country: (str) user's country
    :attr user_image: (str) user's avatar url (if there is one)
    """
    username: str
    country: str = None
    user_image: str = None
