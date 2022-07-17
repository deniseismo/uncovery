import json
import os

from flask import current_app

from uncover import cache


@cache.memoize(timeout=60000)
def load_all_music_genres():
    """
    load a list of music genres from disk
    :return:
    """
    print("loading music genres from disk")
    GENRES_LIST_FILENAME = "genres_list.json"
    GENRES_LIST_PATH = os.path.join(current_app.root_path, 'static/data', GENRES_LIST_FILENAME)
    try:
        with open(GENRES_LIST_PATH) as jsonfile:
            music_genres_list = json.load(jsonfile)
    except (IOError, OSError) as e:
        print(e)
        return []
    print(f"ALL MUSIC GENRES: {music_genres_list}")
    return music_genres_list


def get_suggested_tags(query_tag: str):
    """
    get a list of suggested music genres based on user's input
    :param query_tag: a music tag (genre) to search for
    :return: a list of suggested music genres (genres that the user might have in mind)
    """
    print(f"searching for {query_tag}")
    all_music_genres = load_all_music_genres()
    filtered_tags_list = []
    # check if the input's not empty
    if not query_tag:
        return None
    if len(query_tag) > 98:
        return None
    search_query = query_tag.lower()
    for music_genre in all_music_genres:
        # if a 'tag' consists of the provided input, add it to the final list
        if search_query in music_genre:
            filtered_tags_list.append(music_genre)
    return filtered_tags_list
