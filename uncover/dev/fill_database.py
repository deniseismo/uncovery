import csv
import os
import secrets
import time
import urllib.request
from datetime import datetime

import requests_cache
from PIL import Image
from flask import current_app
from tqdm import tqdm

from uncover import db, create_app
from uncover.helpers.discogs_api import get_album_discogs_id
from uncover.helpers.lastfm_api import lastfm_get_response, lastfm_get_artist_correct_name
from uncover.helpers.main import ultimate_album_image_finder
from uncover.helpers.musicbrainz_api import mb_get_artists_albums, mb_get_album_release_date
from uncover.helpers.spotify_api import spotify_get_artist_id, spotify_get_artists_genres, \
    spotify_get_artists_albums_images, spotify_get_album_id
from uncover.helpers.utilities import timeit
from uncover.models import Artist, Album, Tag

app = create_app()
app.app_context().push()

requests_cache.install_cache()


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


def save_image(image_url):
    if not image_url:
        return None
    try:
        an_image = Image.open(urllib.request.urlopen(image_url))
        if an_image.width >= 900:
            an_image.thumbnail((900, 900), Image.ANTIALIAS)
    except Exception:
        return None
    random_hex = secrets.token_hex(8)
    image_filename = random_hex
    image_path = os.path.join(current_app.root_path, 'static/cover_art_new_batch', image_filename)
    try:
        an_image.convert('RGB').save(f'{image_path}.jpg', quality=95)

        resized_200 = an_image.convert('RGB').resize((200, 200), Image.LANCZOS)
        resized_300 = an_image.convert('RGB').resize((300, 300), Image.LANCZOS)

        resized_200.save(f'{image_path}-size200.jpg', quality=95)
        resized_300.save(f'{image_path}-size300.jpg', quality=95)
    except (OSError, ValueError):
        return None
    return image_filename


@timeit
def database_populate():
    with open('./artists_missing_from_db.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for artist in tqdm(reader):
            print(artist)
            artist_name = artist[0]
            correct_name = lastfm_get_artist_correct_name(artist_name)
            if correct_name:
                artist_name = correct_name
            if Artist.query.filter_by(name=artist_name).first():
                continue
            print(f'ARTIST: {artist_name}')

            artist_albums = mb_get_artists_albums(artist_name, limit=100)
            if not artist_albums:
                artist_albums = spotify_get_artists_albums_images(artist_name)
                if artist_albums:
                    artist_albums = artist_albums['albums']
                else:
                    continue
            artist_entry = Artist(name=artist_name)
            add_artist_music_genres(artist_entry)

            db.session.add(artist_entry)
            db.session.commit()
            artist_id = Artist.query.filter_by(name=artist_name).first().id

            for album in tqdm(artist_albums):
                title = album['title']
                rating = album['rating']
                # spotify_id = spotify_get_album_id(title, artist_name)
                try:
                    mb_id = album['mbid']
                except (KeyError, TypeError):
                    mb_id = None
                try:
                    image_url = album['image']
                except (KeyError, TypeError):
                    image_url = None

                try:
                    alternative_title = album['altenative_name']
                except KeyError:
                    alternative_title = None
                discogs_id = get_album_discogs_id(title, artist_name)
                if not image_url:
                    image_url = ultimate_album_image_finder(title, artist_name, mbid=mb_id)
                cover_art = save_image(image_url)

                if image_url and cover_art:
                    album_entry = Album(artist_id=artist_id,
                                        title=title,
                                        rating=rating,
                                        mb_id=mb_id,
                                        cover_art=cover_art)
                    # if spotify_id:
                    #     album_entry.spotify_id = spotify_id
                    if mb_id:
                        album_entry.mb_id = mb_id
                    if alternative_title:
                        album_entry.alternative_title = alternative_title
                    if discogs_id:
                        album_entry.discogs_id = discogs_id
                    try:
                        release_date = album['release_date']
                    except (KeyError, TypeError):
                        release_date = None
                    if release_date:
                        album_entry.release_date = release_date
                    else:
                        add_album_release_date(album_entry)
                    db.session.add(album_entry)

        db.session.commit()


@timeit
def populate_release_dates():
    all_albums = Album.query.all()
    for album in tqdm(all_albums):
        if album.release_date:
            continue
        if album.mb_id:
            print(f'trying {album.title}, {album.mb_id}')
            release_date = mb_get_album_release_date(album.mb_id)
            if release_date:
                parsed_release_date = datetime.strptime(release_date[:4], '%Y')
                album.release_date = parsed_release_date
                print(f'adding release date ({parsed_release_date}) to ({album.title})')

    db.session.commit()


def add_album_release_date(album):
    """
    :param album: album entry (Album class)
    :return:
    """
    if album.mb_id:
        print(f'trying {album.title}, {album.mb_id}')
        release_date = mb_get_album_release_date(album.mb_id)
        if release_date:
            parsed_release_date = datetime.strptime(release_date[:4], '%Y')
            album.release_date = parsed_release_date
            print(f'adding release date ({parsed_release_date}) to ({album.title})')
    db.session.commit()


def add_artist_music_genres(artist):
    """
    :param artist: artist entry (Artist class)
    :return:
    """
    tags = []
    artist_spotify_id = spotify_get_artist_id(artist.name)
    if artist_spotify_id:
        tags = spotify_get_artists_genres(artist_spotify_id)
    if not tags:
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


@timeit
def populate_music_genres():
    """
    adds music tags to the database
    :return:
    """
    all_artists = Artist.query.all()
    for artist in tqdm(all_artists):
        # search tags via last.fm's API
        artist_spotify_id = spotify_get_artist_id(artist.name)
        tags = []
        if artist_spotify_id:
            # try getting the tags through spotify first
            tags = spotify_get_artists_genres(artist_spotify_id)
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


# def delete_all_tags():
#     tag_entries = Tag.query.all()
#     for tag in tag_entries:
#         db.session.delete(tag)
#     db.session.commit()


def get_all_tags():
    tag_entries = Tag.query.all()
    tags_list = [tag.tag_name for tag in tag_entries]
    import json
    with open('music_tags_all.json', 'w') as f:
        json.dump(tags_list, f, ensure_ascii=False, indent=4)


def populate_spotify_album_ids():
    all_albums = Album.query.filter(Album.id > 16131).all()
    for album in tqdm(all_albums):
        if album.spotify_id:
            print(f'{album.title} already has spotify id, skipping')
            continue
        artist_name = album.artist.name
        album_name = album.title
        spotify_id = spotify_get_album_id(album_name, artist_name)
        if spotify_id:
            print(f'adding {artist_name} - {album_name}: {spotify_id}')
            album.spotify_id = spotify_id
            db.session.commit()

    db.session.commit()


# get_all_tags()

# populate_release_dates()
# populate_music_genres()
# delete_all_tags()
database_populate()

# populate_spotify_album_ids()
