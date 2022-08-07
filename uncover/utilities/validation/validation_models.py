from typing import Optional

from pydantic import validator, BaseModel, Field


class LastFMUserInput(BaseModel):
    """
    validation model for user input in lastfm route; validates username and time period picked by user
    """
    username: str = Field(alias='qualifier')
    time_period: str = Field(alias='option')

    @validator("username", pre=True)
    def is_valid_username(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("username must be a string")
        v = v.strip()
        if not (1 < len(v) < 16):
            raise ValueError("incorrect username length; must be at least 2 characters long and at most 16 chars.")
        return v

    @validator("time_period")
    def is_valid_time_period(cls, v: str) -> str:
        valid_time_periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
        if v not in valid_time_periods:
            raise ValueError("incorrect time period")
        return v


class ArtistUserInput(BaseModel):
    """
    validation model for user input in artist route; validates artist's name and sorting type
    """
    artist_name: str = Field(alias='qualifier')
    sorting: str = Field(alias='option')

    @validator("artist_name", pre=True)
    def is_valid_artist_name(cls, v: str) -> str:
        if not isinstance(v, str):
            raise TypeError("artist name must be a string")
        v = v.strip()
        if len(v) > 98:
            raise ValueError("incorrect username length")
        return v

    @validator("sorting")
    def is_valid_sorting(cls, v: str) -> str:
        valid_sorting_types = ["popular", "latest", "earliest", "shuffle"]
        if v not in valid_sorting_types:
            raise ValueError("incorrect sorting type")
        return v


class ExploreFiltersUserInput(BaseModel):
    """
    validation model for user input in explore route; validates genres, time span & colors picked by user
    """
    genres: Optional[list[str]]
    time_span: Optional[list[int, int]]
    colors: Optional[list[str]]
