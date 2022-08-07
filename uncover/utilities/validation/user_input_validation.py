from typing import Optional

from pydantic import ValidationError

from uncover.utilities.validation.exceptions.validation_exceptions import LastFMUserInputError, ArtistUserInputError, \
    ExploreFiltersUserInputError
from uncover.utilities.validation.validation_models import LastFMUserInput, ArtistUserInput, ExploreFiltersUserInput


def validate_lastfm_user_input(user_input: dict) -> Optional[LastFMUserInput]:
    """
    validate user input for lastfm user handlers (username, time period)
    :param user_input: (dict) user's input with username and time period
    :return: (LastFMUserInput) validated user input
    """
    if not isinstance(user_input, dict):
        raise LastFMUserInputError("incorrect input type")
    try:
        lastfm_user_input = LastFMUserInput(**user_input)
        return lastfm_user_input
    except ValidationError as e:
        print(e.json())
        raise LastFMUserInputError("incorrect username")


def validate_artist_user_input(user_input: dict) -> Optional[ArtistUserInput]:
    """
    validate user input for artist/musician handlers (artist's name, sorting)
    :param user_input: (dict) user's input with artist's name and sorting
    :return: (ArtistUserInput) validated user input
    """
    if not isinstance(user_input, dict):
        raise ArtistUserInputError("incorrect input type")
    try:
        artist_user_input = ArtistUserInput(**user_input)
        return artist_user_input
    except ValidationError as e:
        print(e.json())
        raise ArtistUserInputError("incorrect artist name")


def validate_explore_filters_user_input(user_input: dict) -> Optional[ExploreFiltersUserInput]:
    """
    validate user input for explore filters handlers (genres, colors, time span)
    :param user_input: (dict) user's input with genres, colors & time span picked
    :return: (ExploreFiltersUserInput) validated user input
    """
    if not isinstance(user_input, dict):
        raise ExploreFiltersUserInputError("incorrect input type")
    try:
        explore_filters_user_input = ExploreFiltersUserInput(**user_input)
        return explore_filters_user_input
    except ValidationError as e:
        print(e.json())
        raise ExploreFiltersUserInputError("incorrect filters")
