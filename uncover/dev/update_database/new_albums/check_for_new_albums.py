import csv
import os

from flask import current_app
from tqdm import tqdm

from uncover import create_app
from uncover.models import Artist
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artist_albums_mbids

app = create_app()
app.app_context().push()


def check_music_brainz_for_new_albums(artist_start_id: int = 0, artist_end_id: int = 999999):
    """
    check musicbrainz for new albums (for the most part these are the new releases, or some missing albums);
    only checks albums by artists that are already in database;
    writes newly found albums (only the essential info like artist's name, album's title and musicbrainz id) to .csv
    :param artist_start_id: (int) artist's id in db to start search from (excl.)
    :param artist_end_id: (int) artist's id in db to end search on (excl.)
    """
    artists_filter = Artist.query.filter(Artist.id > artist_start_id).filter(Artist.id < artist_end_id)
    all_artists = artists_filter.all()

    NEW_ALBUMS_FOLDER = 'dev/update_database/new_albums'
    NEW_ALBUMS_FILENAME = "new_albums_found.csv"
    NEW_ALBUMS_PATH = os.path.join(current_app.root_path, NEW_ALBUMS_FOLDER, NEW_ALBUMS_FILENAME)
    fieldnames = ["artist", "album_title", "mb_id"]
    with open(NEW_ALBUMS_PATH, "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writeheader()

    for artist in tqdm(all_artists):
        artist_name = artist.name
        db_albums = artist.albums
        print(artist_name, artist.id)
        albums_from_mb = mb_get_artist_albums_mbids(artist_name)
        if not albums_from_mb:
            albums_from_mb = mb_get_artist_albums_mbids(artist_name, album_type="soundtrack")
            if not albums_from_mb:
                continue
        number_of_albums_in_db = len(db_albums)
        number_of_albums_from_mb = len(albums_from_mb)
        print(f"database: {number_of_albums_in_db}, musicbrainz: {number_of_albums_from_mb}")
        if number_of_albums_in_db != number_of_albums_from_mb:
            print(f"there might be some new albums for Artist({artist_name})")
            mbids_from_database = {original_album.mb_id for original_album in db_albums if original_album.mb_id}
            mbids_from_musicbrainz = albums_from_mb.keys()
            for mb_id in mbids_from_musicbrainz:
                if mb_id not in mbids_from_database:
                    new_album_title = albums_from_mb[mb_id]
                    print(f"new album found", new_album_title)
                    _write_new_album_mb_data_to_csv({
                        "artist": artist_name,
                        "album_title": new_album_title,
                        "mb_id": mb_id
                    })
        print("-" * 5)


def _write_new_album_mb_data_to_csv(album_data: dict) -> None:
    """
    write new album's (essentials from musicbrainz) data to .csv file
    :param album_data: (dict) bare essential from musicbrainz: artist's name, album's title, musicbrainz id
    """
    NEW_ALBUMS_FOLDER = 'dev/update_database/new_albums'
    NEW_ALBUMS_FILENAME = "new_albums_found.csv"
    NEW_ALBUMS_PATH = os.path.join(current_app.root_path, NEW_ALBUMS_FOLDER, NEW_ALBUMS_FILENAME)
    fieldnames = ["artist", "album_title", "mb_id"]
    with open(NEW_ALBUMS_PATH, "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writerow(album_data)
