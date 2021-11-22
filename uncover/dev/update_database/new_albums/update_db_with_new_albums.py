import csv
import os
import secrets
import time
import urllib.request

from PIL import Image
from flask import current_app
from tqdm import tqdm
from uncover import db, create_app
from uncover.dev.color_analyzer.fill_db_colors import add_album_color
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id
from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_alternative_name, \
    mb_get_album_release_date, parse_release_date
from uncover.music_apis.spotify_api.spotify_artist_handlers import spotify_get_artist_id, spotify_get_artists_genres
from uncover.models import Artist, Album, Tag

app = create_app()
app.app_context().push()


def save_image(image_url):
    if not image_url:
        return None
    try:
        an_image = Image.open(urllib.request.urlopen(image_url)).convert('RGB')
        if an_image.width >= 900:
            an_image.thumbnail((900, 900), Image.ANTIALIAS)
    except Exception:
        return None
    random_hex = secrets.token_hex(8)
    image_filename = random_hex
    image_path = os.path.join(current_app.root_path, 'static/cover_art_new_batch', image_filename)
    try:
        # save in original size
        an_image.save(f'{image_path}.jpg', quality=95)

        resized_200 = an_image
        resized_300 = an_image
        if an_image.width > 300:
            # make pictures smaller if the original is bigger than 300 pixels wide
            resized_200 = an_image.resize((200, 200), Image.LANCZOS)
            resized_300 = an_image.resize((300, 300), Image.LANCZOS)

        # save (smaller) copies
        resized_200.save(f'{image_path}-size200.jpg', quality=95)
        resized_300.save(f'{image_path}-size300.jpg', quality=95)
    except (OSError, ValueError):
        return None
    return image_filename


def update_db_with_new_albums():
    fieldnames = ["artist", "album_title", "mb_id"]
    with open("new_albums_ready.csv", encoding="utf-8") as file:
        csvfile = csv.DictReader(file, fieldnames=fieldnames)
        for album in tqdm(csvfile):
            artist_name = album["artist"]
            title = album['album_title']
            print(f"analyzing {artist_name} - {title}")
            title = title.replace("’", "'")
            title_lower = title.lower()
            mb_id = album["mb_id"]
            artist_entry = Artist.query.filter_by(name=artist_name).first()
            if not artist_entry:
                artist_entry = Artist(name=artist_name)
                add_artist_music_genres(artist_entry)
                db.session.add(artist_entry)
                db.session.commit()
                artist_id = Artist.query.filter_by(name=artist_name).first().id
            else:
                artist_id = artist_entry.id
            image_url = ultimate_album_image_finder(title, artist_name, mbid=mb_id)
            cover_art = save_image(image_url)
            if not image_url or not cover_art:
                print("no image found")
                print("-" * 5)
                continue
            print("image found!")
            album_entry = Album(artist_id=artist_id,
                                title=title,
                                mb_id=mb_id,
                                cover_art=cover_art)
            release_date = mb_get_album_release_date(mb_id)
            if release_date:
                print(f"release date: {release_date}")
                release_date = parse_release_date(release_date)
                album_entry.release_date = release_date
            alternative_title = mb_get_album_alternative_name(mb_id)
            if alternative_title:
                print(f"alternative title: {alternative_title}")
                album_entry.alternative_title = alternative_title
            discogs_id = get_album_discogs_id(title, artist_name)
            if discogs_id:
                print(f"discogs id: {discogs_id}")
                album_entry.discogs_id = discogs_id
            rating = lastfm_get_album_listeners(title_lower, artist_name)
            print(f"rating: {rating}")
            album_entry.rating = rating if rating else 0
            add_album_color(album_entry, 'static/cover_art_new_batch')
            db.session.add(album_entry)
            db.session.commit()
            print("-" * 5)


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
    artist_spotify_id = spotify_get_artist_id(artist.name)
    if artist_spotify_id:
        tags = spotify_get_artists_genres(artist_spotify_id)
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


# def testing_some_shit():
#     fieldnames = ["artist", "album_title", "mb_id"]
#     with open("new_albums_found.csv", encoding="utf-8") as file:
#         csvfile = csv.DictReader(file, fieldnames=fieldnames)
#         for album in tqdm(csvfile):
#             artist_name = album["artist"]
#             title = album['album_title']
#             title = title.replace("’", "'")
#             title_lower = title.lower()
#             mb_id = album["mb_id"]
#             print(f"analyzing {artist_name} - {title} - {mb_id}")
#
#
# # testing_some_shit()

update_db_with_new_albums()
