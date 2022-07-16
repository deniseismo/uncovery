from dataclasses import dataclass

from uncover.schemas.info_base import InfoBase


@dataclass
class SpotifyUserAuth(InfoBase):
    spotify_user_id: str = None
    token: str = None


@dataclass
class SpotifyUserProfile(InfoBase):
    username: str
    country: str = None
    user_image: str = None
