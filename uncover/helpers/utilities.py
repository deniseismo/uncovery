import csv
import json
import os
import random
import re
import time

import cyrtranslit
import unidecode

from uncover import cache


def display_failure_art(list_of_images: list):
    """
    picks a random 'failure' cover art from a list
    :return: a 'failure' cover art location
    """
    return random.choice(list_of_images)


@cache.cached(timeout=3600)
def get_failure_images():
    """
    gets the list of all 'failure' art images found in the corresponding folder
    :return:
    """
    images_folder = 'uncover/static/images/fail'
    failure_art_list = [os.path.join('images/fail/', f)
                        for f in os.listdir(images_folder)
                        if os.path.isfile(os.path.join(images_folder, f))]
    return failure_art_list


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def timeit(method):
    """
    times the function
    :param method: function to time
    :return: a number of ms
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def has_cyrillic(name):
    return bool(re.search('[\u0400-\u04FF]', name))


def transliterate(name):
    if not name:
        return None
    translit = cyrtranslit.to_latin(name, 'ru')
    translit = translit.replace("'", "")
    return translit


@cache.memoize(timeout=3600)
def get_filtered_name(album_name: str):
    """
    :param album_name: an album name to filter
    :return: a fitlered name
    """
    # TODO: (mono/stereo) &/and

    # replace some weird characters with normal ones
    a_correct_title = album_name.lower().replace("’", "'")
    patterns = [
        # no special words in brackets
        r"\(.*((\bremaster)|(\banniversary)|(\bEdition)|(\bmix)|(\bdeluxe)|(\bCD)|(\bsoundtrack)).*\)|\[.*\]",
        # no super deluxe
        r"((super)?\s?(deluxe)\s?).*",
        r"((\d+)?\s?(Remaster)\s?).*",
        # r"((\d+)?\s?(Complete)\s?).*", # TODO: fix 'complete', removes too many words rn
        r"((\d+)?\s?(Bonus Tracks)\s?).*",
        r"((\d+)?\s?(International Version)\s?).*",
        r"\d+?(th)?\s?Anniversary\s?\w*",
        # no weird characters
        r"[“”:\(\)\":…]"
    ]
    for pattern in patterns:
        a_correct_title = re.sub(pattern, '', a_correct_title, flags=re.IGNORECASE)
    # finally removes some trailing hyphens and/or whitespaces
    ultimate_filtered_name = a_correct_title.strip('-').strip()
    return ultimate_filtered_name


@cache.memoize(timeout=36000)
def remove_punctuation(name: str):
    if not name:
        return None
    pattern = "[^\w\s]"
    return re.sub(pattern, '', name, flags=re.IGNORECASE)


@cache.memoize(timeout=3600)
def get_filtered_names_list(a_name: str):
    """
    filters out some articles, incorrect symbols & redundant words (e.g. Deluxe Edition)
    :param a_name: album's title
    :return: a list of filtered names
    """
    if not a_name:
        return None
    filtered_names = set()
    a_correct_title = a_name.lower().replace("“", "").replace("”", "").replace(":", "").replace("’", "'")
    no_articles = a_correct_title.replace("the ", "")
    with_and = a_correct_title.replace(" and ", " & ")
    with_ampersand = a_correct_title.replace(" & ", " and ")

    with_and_no_articles = no_articles.replace("  and", " & ")
    with_with_ampersand_no_articles = no_articles.replace(" & ", " and ")
    after_regex = get_filtered_name(a_name)
    after_regex_no_articles = after_regex.replace('the ', '')
    no_yo = a_correct_title.replace("ё", 'е')
    eszett = a_correct_title.replace("ß", 'ss')
    ae = a_correct_title.replace("æ", 'ae')
    oe = a_correct_title.replace("œ", "oe")
    # no_accents = unicodedata.normalize('NFD', a_correct_title)
    # no_accents = no_accents.encode('ascii', 'ignore')
    # no_accents = no_accents.decode("utf-8")
    no_accents = unidecode.unidecode(a_correct_title)
    no_punctuation = remove_punctuation(a_correct_title)
    print(f'no accents: {no_accents}')
    filtered_names.add(a_correct_title)
    filtered_names.add(no_articles)
    filtered_names.add(after_regex)
    filtered_names.add(after_regex_no_articles)
    filtered_names.add(with_and)
    filtered_names.add(with_ampersand)
    filtered_names.add(with_and_no_articles)
    filtered_names.add(with_with_ampersand_no_articles)
    filtered_names.add(no_yo)
    filtered_names.add(no_accents)
    filtered_names.add(oe)
    filtered_names.add(ae)
    filtered_names.add(eszett)
    filtered_names.add(no_punctuation)
    print(list(filtered_names))
    return list(filtered_names)


def log_artist_missing_from_db(artist_name: str):
    """
    logs artist's name to the csv file of all the artists not yet found in db
    :param artist_name: artist's name
    """
    try:
        with open('uncover/logging/artists_missing_from_db.csv', 'r', newline='', encoding='utf-8') as file:
            contents = file.read()
    except (IOError, OSError):
        return False
    if artist_name in contents:
        print(f"{artist_name}'s already there")
        # no need to add the artist
        return False
    with open('uncover/logging/artists_missing_from_db.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([artist_name])
        return True
