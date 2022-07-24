import csv
import time

from tqdm import tqdm
from uncover import create_app, db
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response
from uncover.music_apis.spotify_api.spotify_artist_handlers import get_spotify_artist_info, spotify_get_artists_genres
from uncover.utilities.misc import timeit
from uncover.models import Artist, tags, Tag

app = create_app()
app.app_context().push()


def merge_hip_hop_genres():
    hip_space_hop_artists = Artist.query \
        .join(tags, (tags.c.artist_id == Artist.id)).join(Tag, (Tag.id == tags.c.tag_id)) \
        .filter(Tag.tag_name == 'hip hop')

    hip_hop_artists = Artist.query \
        .join(tags, (tags.c.artist_id == Artist.id)).join(Tag, (Tag.id == tags.c.tag_id)) \
        .filter(Tag.tag_name == 'hip-hop')

    list1_as_set = set(hip_hop_artists.all())

    intersection = list1_as_set.intersection(hip_space_hop_artists.all())

    intersection_as_list = list(intersection)

    print(intersection_as_list)
    for artist in hip_space_hop_artists.all():
        print(artist)
        hip_hop_tag = Tag.query.filter_by(tag_name='hip-hop').first()
        hip_hop_tag.artists.append(artist)
        db.session.commit()


def remove_bad_words_from_tags():
    with open('bad_words.csv', newline='') as f:
        reader = csv.reader(f)
        list_of_bad_words = [row[0] for row in reader]
        tag_entries = Tag.query.all()
        tags_list = [tag.tag_name for tag in tag_entries]
        for tag in tags_list:
            # for bad_word in list_of_bad_words:
            #     if bad_word in tag:
            #         print(tag)
            if tag in list_of_bad_words:
                print(tag)
                # tagjke = Tag.query.filter_by(tag_name=tag).first()
                # print(tagjke)
                # db.session.delete(tagjke)
                # db.session.commit()


def get_artist_tags(artist_name: str):
    filter_query = Tag.query.join(tags, (Tag.id == tags.c.tag_id)) \
        .join(Artist, (tags.c.artist_id == Artist.id)) \
        .filter(Artist.name == artist_name).all()
    return filter_query


def remove_artist_from_genre(artist_name: str, genre_name: str):
    artist_entry = Artist.query.filter_by(name=artist_name).first()
    genre_entry = Tag.query.filter_by(tag_name=genre_name).first()
    if not artist_entry:
        print(f'{artist_entry} not found')
        return False
    if not genre_entry:
        print(f'{genre_entry} not found')
        return False
    print(f'{artist_name}, {genre_name} found!')
    try:
        genre_entry.artists.remove(artist_entry)
        print(f'{artist_entry}, is about to be deleted from {genre_entry}')
        db.session.commit()
    except ValueError as e:
        print(f'{artist_entry} is not in {genre_entry}')
        print(e)
        return False


def get_all_tags():
    tag_entries = Tag.query.all()
    tags_list = [tag.tag_name for tag in tag_entries]
    import json
    with open('music_tags_all.json', 'w') as f:
        json.dump(tags_list, f, ensure_ascii=False, indent=4)


def lookup_tags(artist: str):
    """
    :param artist: musician/band
    :return: top 3 tags from the given artist in the form of a string
    """
    response = lastfm_get_response({
        'method': 'artist.getTopTags',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        tags = [tag['name'].lower() for tag in response.json()['toptags']['tag'][:3]]
    except (KeyError, IndexError, TypeError):
        return None

    # tags_string = ', '.join(tags)

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.4)
    return tags


def add_artist_music_genres(artist):
    """
    :param artist: artist entry (Artist class)
    :return:
    """
    tags = []
    artist_spotify_entry = get_spotify_artist_info(artist.name)
    if not artist_spotify_entry:
        return False
    tags = spotify_get_artists_genres(artist_spotify_entry)
    if not tags:
        tags = lookup_tags(artist.name)
    if tags:
        for tag in tags:
            if tag == 'hip hop':
                tag = 'hip-hop'
            tag_entry = Tag.query.filter_by(tag_name=tag).first()
            if not tag_entry:
                # add the tag if not exists
                tag_entry = Tag(tag_name=tag)
                db.session.add(tag_entry)
                db.session.commit()
            # append artist to the tag, thus creating the many-to-many association between tags & artists
            tag_entry.artists.append(artist)
        db.session.commit()


@timeit
def populate_music_genres():
    """
    adds music tags to the database
    :return:
    """
    all_artists = Artist.query.all()
    for artist in tqdm(all_artists):
        # search tags via last.fm's API
        artist_spotify_entry = get_spotify_artist_info(artist.name)
        tags = []
        if artist_spotify_entry:
            # try getting the tags through spotify first
            tags = spotify_get_artists_genres(artist_spotify_entry)
        if not tags:
            # if spotify hasn't found any tags, try getting through lastfm
            tags = lookup_tags(artist.name)
        if tags:
            for tag in tags:
                tag_entry = Tag.query.filter_by(tag_name=tag).first()
                if not tag_entry:
                    # add the tag if not exists
                    tag_entry = Tag(tag_name=tag)
                    db.session.add(tag_entry)
                    db.session.commit()
                # append artist to the tag, thus creating the many-to-many association between tags & artists
                tag_entry.artists.append(artist)

    db.session.commit()
