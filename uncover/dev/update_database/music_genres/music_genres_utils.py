import csv
import json
import os

from flask import current_app
from sqlalchemy import func

from uncover import db, create_app
from uncover.models import Tag, Artist, tags

app = create_app()
app.app_context().push()


def write_all_music_genres_to_file() -> None:
    """
    write all music genres names from database to .csv file
    """
    tag_entries = Tag.query.all()
    tags_list = [tag.tag_name for tag in tag_entries]
    MUSIC_GENRES_FOLDER = 'dev/update_database/music_genres'
    MUSIC_GENRES_FILENAME = "bad_words.csv"
    MUSIC_GENRES_PATH = os.path.join(current_app.root_path, MUSIC_GENRES_FOLDER, MUSIC_GENRES_FILENAME)
    with open(MUSIC_GENRES_PATH, 'w') as f:
        json.dump(tags_list, f, ensure_ascii=False, indent=4)


def get_artist_music_genres_from_db(artist_name: str) -> list[Tag]:
    """
    get a list of music genres (Tag objects) for a particular artist from database
    :param artist_name: artist's name
    :return: (list[Tag]) a list of music genres (Tag)
    """
    filter_query = Tag.query.join(tags, (Tag.id == tags.c.tag_id)) \
        .join(Artist, (tags.c.artist_id == Artist.id)) \
        .filter(Artist.name == artist_name).all()
    return filter_query


def delete_music_genres_with_bad_words_from_db() -> None:
    """
    deletes music genres from database with explicit/bad/obscene words in them
    """
    MUSIC_GENRES_FOLDER = 'dev/update_database/music_genres'
    BAD_WORDS_FILENAME = "bad_words.csv"
    BAD_WORDS_PATH = os.path.join(current_app.root_path, MUSIC_GENRES_FOLDER, BAD_WORDS_FILENAME)
    with open(BAD_WORDS_PATH, newline='') as f:
        reader = csv.reader(f)
        list_of_bad_words = [row[0] for row in reader]
        tag_entries = Tag.query.all()
        tags_list = [tag.tag_name for tag in tag_entries]
        for tag in tags_list:
            if tag in list_of_bad_words:
                print(tag)
                bad_tag = Tag.query.filter_by(tag_name=tag).first()
                db.session.delete(bad_tag)
                db.session.commit()


def remove_music_genres_with_bad_words_in_them(music_genres: set[str]) -> set[str]:
    """
    removes music genres with bad words in them from a set of music genres
    :param music_genres: (set) of music genres (music genre names)
    :return: a set of music genres without genres with bad words
    """
    MUSIC_GENRES_FOLDER = 'dev/update_database/music_genres'
    BAD_WORDS_FILENAME = "bad_words.csv"
    BAD_WORDS_PATH = os.path.join(current_app.root_path, MUSIC_GENRES_FOLDER, BAD_WORDS_FILENAME)
    with open(BAD_WORDS_PATH, newline='') as f:
        reader = csv.reader(f)
        list_of_bad_words = [row[0] for row in reader]
        for music_genre in set(music_genres):
            if music_genre in list_of_bad_words:
                music_genres.remove(music_genre)
        return music_genres


def get_artists_having_fewer_than_n_music_genres(
        number_of_music_genres: int = 4,
        artist_start_id: int = 0
) -> list[Artist]:
    q = db.session.query(Artist). \
        join(Artist.music_genres). \
        group_by(Artist). \
        having(func.count(Tag.id) < number_of_music_genres).filter(Artist.id > artist_start_id)
    artists_having_fewer_than_n_music_genres = q.all()
    return artists_having_fewer_than_n_music_genres


def fix_hip_hop_in_music_genres_set(music_genres: set[str]) -> set[str]:
    """
    change "hip hop" to "hip-hop" in a set of music genres (names)
    :param music_genres: (set[str]) a set of music genre names
    :return: (set[str]) set of names with 'hip hop' fixed → 'hip-hop'
    """
    # hip hop → hip-hop
    HIP_HOP_WITH_SPACE = "hip hop"
    HIP_HOP_WITH_HYPHEN = "hip-hop"
    if HIP_HOP_WITH_SPACE in music_genres:
        music_genres.remove(HIP_HOP_WITH_SPACE)
        music_genres.add(HIP_HOP_WITH_HYPHEN)
    return music_genres
