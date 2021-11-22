import csv
import os

import requests_cache
from flask import current_app
from tqdm import tqdm
from uncover import create_app
from uncover.dev.color_analyzer.get_dominant_colors import get_image_dominant_color
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artist_albums_v2
from uncover.models import Artist, Album

app = create_app()
app.app_context().push()

requests_cache.install_cache()


def check_music_brainz_for_new_albums():
    # get all artists from db
    # lana = Artist.query.get(769)
    # avalanches = Artist.query.get(1171)
    # all_artists = [lana, avalanches]
    all_artists = Artist.query.all()
    fieldnames = ["artist", "album_title", "mb_id"]
    with open("new_albums_found.csv", "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writeheader()

    for artist in tqdm(all_artists):
        db_albums = artist.albums
        artist_name = artist.name
        print(artist_name)
        albums_from_mb = mb_get_artist_albums_v2(artist_name)
        if not albums_from_mb:
            continue
        if len(albums_from_mb) > len(db_albums):
            print(f"potential new albums found for {artist_name}")
            original_mb_ids = [original_album.mb_id for original_album in db_albums if original_album.mb_id]
            new_mb_ids = [key for key in albums_from_mb.keys()]
            for mb_id in new_mb_ids:
                if mb_id not in original_mb_ids:
                    new_album_title = albums_from_mb[mb_id]
                    print(f"new album found", new_album_title)
                    with open("new_albums_found.csv", "a", encoding="utf-8") as file:
                        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
                        data = {
                            "artist": artist_name,
                            "album_title": new_album_title,
                            "mb_id": mb_id
                        }
                        csvfile.writerow(data)
        print("-" * 5)


# check_music_brainz_for_new_albums()

# 51447
def get_new_albums_from_db(album_id_start):
    albums_to_get = Album.query.filter(Album.id > album_id_start).all()
    fieldnames = ["artist", "album_title", "rating", "alternative_title", "mb_id", "discogs_id", "release_date",
                  "album_cover_color"]
    with open("transfer_new_albums.csv", "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writeheader()
    for album in tqdm(albums_to_get):
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

        with open("transfer_new_albums.csv", "a", encoding="utf-8") as file:
            csvfile = csv.DictWriter(file, fieldnames=fieldnames)
            data = {
                "artist": artist_name,
                "album_title": album_title,
                "rating": rating,
                "alternative_title": alternative_title,
                "mb_id": mb_id,
                "discogs_id": discogs_id,
                "release_date": release_date,
                "album_cover_color": album_cover_color
            }
            print(data)
            csvfile.writerow(data)


def get_album_colors(image_filename):
    folder = 'static/cover_art_new_batch'
    image_path = os.path.join(current_app.root_path, folder,
                              image_filename) + '-size200.jpg'
    colors = get_image_dominant_color(image_path)
    if not colors:
        colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
    return colors


get_new_albums_from_db(52910)
