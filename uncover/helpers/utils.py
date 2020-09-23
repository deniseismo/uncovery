import json
import random
import re
import time


def display_failure_art(list_of_images):
    """
    picks a random 'failure' cover art from a list
    :return: a 'failure' cover art location
    """
    return random.choice(list_of_images)


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

@timeit
def get_filtered_name(album_name):
    """
    :param album_name: an album name to filter
    :return: a fitlered name
    """
    # TODO: (remaster) (limited edition) (remastered) (edition, anniversary)
    a_correct_title = album_name.lower().replace("“", "") \
        .replace("”", "").replace(":", "").replace("’", "'")
    no_deluxe_pattern = r"((super)?\s?(deluxe)\s?).*"
    no_deluxe_2_pattern = r"\(\S*\s*deluxe\w*\)"
    no_remaster_pattern = r"((\d+)?\s?(Remaster)\s?).*"
    no_remaster_2_pattern = r"\(\S*\s*Remaster\w*\)"
    no_anniversary_pattern = r"\(\S*\s*anniversary\w*\)"
    no_anniversary_2_pattern = r"\d+?(th)?\s?Anniversary\s?\w*"
    no_edition_pattern = r"\(\S*\s*edition\w*\)"
    no_weird_characters_pattern = r'[\(\)\":]'
    no_deluxe = re.sub(no_deluxe_pattern, '', a_correct_title, flags=re.IGNORECASE)
    no_remaster = re.sub(no_remaster_pattern, '', no_deluxe, flags=re.IGNORECASE)
    no_deluxe_2 = re.sub(no_deluxe_2_pattern, '', no_remaster, flags=re.IGNORECASE)
    no_remaster_2 = re.sub(no_remaster_2_pattern, '', no_deluxe_2, flags=re.IGNORECASE)
    no_anniversary = re.sub(no_anniversary_pattern, '', no_remaster_2, flags=re.IGNORECASE)
    no_edition = re.sub(no_edition_pattern, '', no_anniversary, flags=re.IGNORECASE)
    no_anniversary_2 = re.sub(no_anniversary_2_pattern, '', no_edition, flags=re.IGNORECASE)
    ultimate_filtered_name = re.sub(no_weird_characters_pattern, '', no_anniversary_2).strip()
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
    filtered_names.add(a_correct_title)
    filtered_names.add(no_articles)
    filtered_names.add(after_regex)
    return list(filtered_names)
