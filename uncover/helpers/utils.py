import json
import random
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


def filter_album_name(album_name):
    """
    filters out some articles, incorrect symbols & redundant words (e.g. Deluxe Edition)
    :param album_name: album's title
    :return: a list of filtered names
    """
    filtered_names = set()
    a_correct_title = album_name.lower().replace("“", "").replace("”", "").replace(":", "")
    filtered_names.add(a_correct_title)
    filtered_names.add(a_correct_title.replace("deluxe edition", ""))
    filtered_names.add(a_correct_title.replace("deluxe version", ""))
    filtered_names.add(a_correct_title.replace(" deluxe", ""))
    filtered_names.add(a_correct_title.replace(" remastered", ""))
    filtered_names.add(a_correct_title.replace("the ", ""))
    return list(filtered_names)
