import csv
import json
import os
import random
import re
import time


def display_failure_art(list_of_images):
    """
    picks a random 'failure' cover art from a list
    :return: a 'failure' cover art location
    """
    return random.choice(list_of_images)


def get_failure_images():
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


def get_filtered_name(album_name):
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
        r"\d+?(th)?\s?Anniversary\s?\w*",
        # no weird characters
        r"[“”:\(\)\":…]"
    ]
    for pattern in patterns:
        a_correct_title = re.sub(pattern, '', a_correct_title, flags=re.IGNORECASE)
    # finally removes some trailing hyphens and/or whitespaces
    ultimate_filtered_name = a_correct_title.strip('-').strip()
    return ultimate_filtered_name


def get_filtered_names_list(album_name):
    """
    filters out some articles, incorrect symbols & redundant words (e.g. Deluxe Edition)
    :param album_name: album's title
    :return: a list of filtered names
    """
    filtered_names = set()
    a_correct_title = album_name.lower().replace("“", "").replace("”", "").replace(":", "").replace("’", "'")
    no_articles = a_correct_title.replace("the ", "")
    after_regex = get_filtered_name(album_name)
    after_regex_no_articles = after_regex.replace('the ', '')
    filtered_names.add(a_correct_title)
    filtered_names.add(no_articles)
    filtered_names.add(after_regex)
    filtered_names.add(after_regex_no_articles)
    return list(filtered_names)


def log_artist_missing_from_db(artist_name: str):
    """
    logs artist's name to the csv file of all the artists not yet found in db
    :param artist_name: artist's name
    """
    with open('uncover/logging/artists_missing_from_db.csv', 'r', newline='', encoding='utf-8') as file:
        contents = file.read()
    if artist_name in contents:
        print(f"{artist_name}'s already there")
        # no need to add the artist
        return None
    with open('uncover/logging/artists_missing_from_db.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([artist_name])
        return True

