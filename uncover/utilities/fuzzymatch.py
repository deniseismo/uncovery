from fuzzywuzzy import fuzz


def fuzzy_match_artist(artist_1: str, artist_2: str, strict: bool = False) -> bool:
    """
    decide whether two artists names is the same artist name, e.g. The Notorious B.I.G. = Notorious BIG
    :param artist_1: (str) artist's name
    :param artist_2: (str) artist's name
    :param strict: make fuzzy matching stricter
    :return: (bool) True if two names are similar enough, False otherwise
    """
    ratio = fuzz.ratio(artist_1, artist_2)
    if strict:
        return ratio > 92
    partial_ratio = fuzz.partial_ratio(artist_1, artist_2)
    set_ratio = fuzz.token_set_ratio(artist_1, artist_2)
    return ratio > 92 or partial_ratio > 90 or set_ratio > 95
