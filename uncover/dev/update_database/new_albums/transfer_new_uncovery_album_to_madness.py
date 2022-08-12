import csv
import os

import requests_cache
from flask import current_app
from tqdm import tqdm

from uncover import create_app
from uncover.dev.color_analyzer.get_dominant_colors import get_album_colors
from uncover.models import Album

app = create_app()
app.app_context().push()

requests_cache.install_cache()


def prepare_new_albums_for_madnessbracket(album_id_start: int) -> None:
    """
    get all the needed info about new albums from database to be transferred to madnessbracket;
    writes info to .csv [transfer_new_albums.csv]
    :param album_id_start: (int) album id (in database) to start from (excl.)
    :return:
    """
    albums_to_transfer = Album.query.filter(Album.id > album_id_start).all()

    TRANSFER_ALBUMS_FOLDER = 'dev/update_database/new_albums'
    TRANSFER_ALBUMS_FILENAME = "transfer_new_albums.csv"
    TRANSFER_ALBUMS_PATH = os.path.join(current_app.root_path, TRANSFER_ALBUMS_FOLDER, TRANSFER_ALBUMS_FILENAME)
    fieldnames = ["artist", "album_title", "rating", "alternative_title", "mb_id", "discogs_id", "release_date",
                  "album_cover_color"]
    with open(TRANSFER_ALBUMS_PATH, "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writeheader()
    for album in tqdm(albums_to_transfer):
        print(album, album.id)
        artist_name = album.artist.name
        album_title = album.title
        rating = album.rating
        alternative_title = album.alternative_title
        mb_id = album.mb_id
        discogs_id = album.discogs_id
        release_date = album.release_date
        album_cover_art_filename = album.cover_art
        album_cover_color = get_album_colors(album_cover_art_filename)
        _write_new_album_data_to_csv({
            "artist": artist_name,
            "album_title": album_title,
            "rating": rating,
            "alternative_title": alternative_title,
            "mb_id": mb_id,
            "discogs_id": discogs_id,
            "release_date": release_date,
            "album_cover_color": album_cover_color
        })


def _write_new_album_data_to_csv(album_data: dict) -> None:
    """
    write new album's (necessary for transferring) data to .csv file
    :param album_data: (dict) all the necessary data about album for transferring it to madnessbracket
    """
    TRANSFER_ALBUMS_FOLDER = 'dev/update_database/new_albums'
    TRANSFER_ALBUMS_FILENAME = "transfer_new_albums.csv"
    TRANSFER_ALBUMS_PATH = os.path.join(current_app.root_path, TRANSFER_ALBUMS_FOLDER, TRANSFER_ALBUMS_FILENAME)
    fieldnames = ["artist", "album_title", "rating", "alternative_title", "mb_id", "discogs_id", "release_date",
                  "album_cover_color"]
    with open(TRANSFER_ALBUMS_PATH, "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writerow(album_data)


#prepare_new_albums_for_madnessbracket(56009)
