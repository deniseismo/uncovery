import re
from typing import Optional

import cyrtranslit
import unidecode

from uncover import cache


def has_cyrillic(name: str) -> bool:
    return bool(re.search('[\u0400-\u04FF]', name))


def transliterate(name: str) -> Optional[str]:
    if not name:
        return None
    transliterated_name = cyrtranslit.to_latin(name, 'ru')
    transliterated_name = transliterated_name.replace("'", "")
    return transliterated_name


@cache.memoize(timeout=3600)
def get_filtered_name(name_to_filter: str) -> str:
    """
    filter/remove all kinds of poorly written/worded unnecessary music tags
    (e.g. [Mono version], Anniversary Edition, Bonus Tracks, etc.) from album's title
    :param name_to_filter: (str) a string (name) to filter (album/ep/single's title)
    :return: (str) filtered name
    """
    # replace some weird characters with normal ones
    filtered_name = name_to_filter.lower().replace("’", "'")
    patterns = [
        # no special words in brackets
        r"\(.*((\bremaster)|(\banniversary)|(\bEdition)|(\bmix)|(\bdeluxe)|(\bCD)|(\bsoundtrack)|(\bComplete)).*\)|\[.*\]",
        # no super deluxe, remaster, etc.
        r"((super)?\s?(deluxe)\s?).*",
        r"((\d+)?\s?(Remaster)\s?).*",
        r"((\d+)?\s?(Bonus Tracks)\s?).*",
        r"((\d+)?\s?(International Version)\s?).*",
        r"\d+?(th)?\s?Anniversary\s?\w*",
        # no weird characters
        r"[“”:\(\)\":…]"
    ]
    for pattern in patterns:
        filtered_name = re.sub(pattern, '', filtered_name, flags=re.IGNORECASE)
    # removes some trailing hyphens and/or whitespaces
    filtered_name = _remove_trailing_hyphens(filtered_name)
    filtered_name = _remove_trailing_spaces(filtered_name)
    return filtered_name


def _remove_trailing_hyphens(name: str) -> str:
    return name.strip('-')


def _remove_trailing_spaces(name: str) -> str:
    return name.strip()


@cache.memoize(timeout=36000)
def remove_punctuation(name: str):
    if not name:
        return None
    pattern = "[^\w\s]"
    return re.sub(pattern, '', name, flags=re.IGNORECASE)


@cache.memoize(timeout=3600)
def get_filtered_names_list(name_to_filter: str) -> Optional[list[str]]:
    """
    get a list of possible variations of filtered and/or unfiltered titles;
    e.g. with or without "The", & spelled as 'and' or vice versa,
        with simplified versions of 'complex' characters like ё, ß or œ, etc.
    :param name_to_filter: album's title
    :return: a list of filtered names
    """
    if not name_to_filter:
        return None
    filtered_names = set()
    filtered_name = get_filtered_name(name_to_filter)
    correct_title = name_to_filter.lower().replace("“", "").replace("”", "").replace(":", "").replace("’", "'")
    no_articles = correct_title.replace("the ", "")
    with_and = correct_title.replace(" and ", " & ")
    with_ampersand = correct_title.replace(" & ", " and ")
    no_articles_with_and = no_articles.replace("  and", " & ")
    no_articles_with_ampersand = no_articles.replace(" & ", " and ")
    filtered_name_no_articles = filtered_name.replace('the ', '')
    simplified_yo = correct_title.replace("ё", 'е')
    simplified_eszett = correct_title.replace("ß", 'ss')
    simplified_ae = correct_title.replace("æ", 'ae')
    simplified_oe = correct_title.replace("œ", "oe")
    # no_accents = unicodedata.normalize('NFD', correct_title)
    # no_accents = no_accents.encode('ascii', 'ignore')
    # no_accents = no_accents.decode("utf-8")
    no_accents = unidecode.unidecode(correct_title)
    no_punctuation = remove_punctuation(correct_title)
    filtered_names.update(
        [
            correct_title,
            no_articles,
            filtered_name,
            filtered_name_no_articles,
            with_and,
            with_ampersand,
            no_articles_with_and,
            no_articles_with_ampersand,
            simplified_yo,
            no_accents,
            simplified_oe,
            simplified_ae,
            simplified_eszett,
            no_punctuation
        ]
    )
    return list(filtered_names)


def fix_artist_name(artist_name: str) -> str:
    """
    fix weird apostrophes and hyphens
    :param artist_name:
    :return: fixed artist_name
    """
    fixed_artist_name = fix_hyphen(fix_quot_marks(artist_name)).replace(',', '')
    return fixed_artist_name


def fix_quot_marks(name: str) -> str:
    """
    fixes quotations marks, apostrophes (’, “, ”)
    """
    fixed_name = name.replace("’", "'").replace("‘", "'").replace('“', '"').replace('”', '"')
    return fixed_name


def fix_hyphen(string_to_fix: str) -> str:
    """replaces weird hyphen sign (often found on MusicBrainz) with the normal one (hyphen-minus)
    Args:
        string_to_fix (str): fixed string
    """
    return string_to_fix.replace("‐", "-")


def remove_leading_slash(filename: str) -> str:
    """
    removes leading slashes "/" from the string (used for better path joining)
    :param filename: (str)
    :return: string with no "/" at the beginning
    """
    return filename.lstrip("/")
