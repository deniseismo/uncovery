import csv
import os
from typing import Optional

import requests_cache
from flask import current_app
from tqdm import tqdm

from uncover import create_app
from uncover import db
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.dev.image_processing.color_processing.db_color_manipulations import get_album_entry_image_salient_colors, \
    add_album_entry_colors_to_db
from uncover.dev.image_processing.process_images import save_image_from_external_source
from uncover.dev.update_database.music_genres.add_music_genres import add_music_genres_to_artist, \
    collect_all_music_genres_for_artist
from uncover.models import Artist, Album
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_release_date
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artists_albums
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_artists_albums
from uncover.music_apis.spotify_api.spotify_artist_handlers import get_artist_spotify_name_by_name
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.convert_values import parse_release_date

app = create_app()
app.app_context().push()

requests_cache.install_cache()


def update_db_with_new_artists() -> None:
    """
    updates database with new artists from .csv file; adds artists albums, artists genres, the whole shebang.
    """
    NEW_ARTISTS_FILENAME = "artists_missing_from_db.csv"
    NEW_ARTISTS_PATH = os.path.join(current_app.root_path, 'dev/update_database/new_artists', NEW_ARTISTS_FILENAME)
    try:
        with open(NEW_ARTISTS_PATH, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for artist in tqdm(reader):
                artist_name = artist[0]
                print(f"processing new artist: ({artist_name})")
                correct_name = lastfm_get_artist_correct_name(artist_name)
                if correct_name:
                    artist_name = correct_name
                if Artist.query.filter_by(name=artist_name).first():
                    print(f"{artist_name} is already in the database")
                    continue
                print(f'new Artist({artist_name})')
                artist_albums = _collect_all_artist_albums(artist_name)
                if not artist_albums:
                    continue
                artist_entry = Artist(name=artist_name)
                music_genres = collect_all_music_genres_for_artist(artist_name)
                if music_genres:
                    add_music_genres_to_artist(music_genres, artist_entry)
                artist_spotify_name = get_artist_spotify_name_by_name(artist_name)
                if artist_spotify_name and artist_spotify_name != artist_name:
                    artist_entry.spotify_name = artist_spotify_name
                db.session.add(artist_entry)
                db.session.commit()

                artist_id = Artist.query.filter_by(name=artist_name).first().id

                add_artist_albums_to_database(artist_albums, artist_name, artist_id)

            db.session.commit()

    except (IOError, OSError) as e:
        print(e)


def add_artist_albums_to_database(artist_albums: list[AlbumInfo], artist_name: str, artist_id: int) -> None:
    """
    add new artists albums given a list of AlbumInfo albums and artist's name and their id in db
    :param artist_albums: (list[AlbumInfo] a list of AlbumInfo albums with _most_ of the needed info
    :param artist_name: (str) artist's name
    :param artist_id: artist's id in db
    """
    for album_info in artist_albums:
        print(album_info.title)
        album_image_url = album_info.image
        album_release_date = parse_release_date(album_info.year) if album_info.year else None
        discogs_id = get_album_discogs_id(album_info.title, artist_name)
        if not album_image_url:
            album_image_url = ultimate_album_image_finder(album_info.title, artist_name, mbid=album_info.mbid)
        if not album_image_url:
            continue
        cover_art = save_image_from_external_source(album_image_url)
        print(cover_art)
        if not cover_art:
            continue
        album_entry = Album(artist_id=artist_id,
                            title=album_info.title,
                            rating=album_info.rating,
                            cover_art=cover_art)
        if album_info.mbid:
            album_entry.mb_id = album_info.mbid
        if album_info.alternative_name:
            album_entry.alternative_title = album_info.alternative_name
        if discogs_id:
            album_entry.discogs_id = discogs_id
        if not album_release_date:
            album_release_date = mb_get_album_release_date(album_info.mbid)
            if album_release_date:
                album_release_date = parse_release_date(album_release_date)
        if album_release_date:
            album_entry.release_date = album_release_date
        album_colors = get_album_entry_image_salient_colors(album_entry, folder_type="new")
        if album_colors:
            add_album_entry_colors_to_db(album_entry, album_colors)
        db.session.add(album_entry)
        db.session.commit()


def _collect_all_artist_albums(artist_name: str) -> Optional[list[AlbumInfo]]:
    artist_albums = mb_get_artists_albums(artist_name, limit=100)
    if not artist_albums:
        print("didn't find studio albums on musicbrainz")
        artist_albums = mb_get_artists_albums(artist_name, limit=100, album_type="soundtrack")
        if not artist_albums:
            print("didn't find soundtrack albums on musicbrainz")
            artist_albums = spotify_get_artists_albums(artist_name)
            if not artist_albums:
                print("didn't find any albums, even on spotify")
                return None
    return artist_albums


update_db_with_new_artists()
