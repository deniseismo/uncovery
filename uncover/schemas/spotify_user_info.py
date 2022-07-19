from dataclasses import dataclass
from typing import Optional

from uncover.schemas.info_base import InfoBase


@dataclass
class SpotifyUserAuth(InfoBase):
    spotify_user_id: Optional[str] = None
    token: Optional[str] = None


@dataclass
class SpotifyUserProfile(InfoBase):
    username: str
    country: str = None
    user_image: str = None
