import csv
import os

from flask import current_app
from tqdm import tqdm

from uncover import db, create_app
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.dev.color_analyzer.fill_db_colors import add_album_color
from uncover.dev.image_processing.process_images import save_image_from_external_source
from uncover.dev.update_database.music_genres.add_music_genres import collect_all_music_genres_for_artist, \
    add_music_genres_to_artist
from uncover.models import Artist, Album
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id
from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_alternative_name, \
    mb_get_album_release_date
from uncover.utilities.convert_values import parse_release_date
from uncover.utilities.name_filtering import fix_quot_marks

app = create_app()
app.app_context().push()


def update_db_with_new_albums() -> None:
    """
    updates database with newly found albums (for the most part these are the new releases, or some missing albums);
    uses a .csv file [new_albums_ready.csv] with most of the info about the albums prepared (we must find and/or pick new albums beforehand)
    """
    NEW_ALBUMS_FILENAME = "new_albums_ready.csv"
    NEW_ALBUMS_PATH = os.path.join(current_app.root_path, 'dev/update_database/new_albums', NEW_ALBUMS_FILENAME)
    fieldnames = ["artist", "album_title", "mb_id"]
    try:
        with open(NEW_ALBUMS_PATH, encoding="utf-8") as file:
            csvfile = csv.DictReader(file, fieldnames=fieldnames)
            for album in tqdm(csvfile):
                artist_name = album["artist"]
                album_title = album['album_title']
                album_title = fix_quot_marks(album_title)
                print(f"searching info for new Album({album_title}) by Artist({artist_name})")
                mb_id = album["mb_id"]
                artist_entry = Artist.query.filter_by(name=artist_name).first()
                if not artist_entry:
                    artist_entry = Artist(name=artist_name)
                    music_genres = collect_all_music_genres_for_artist(artist_name)
                    if music_genres:
                        add_music_genres_to_artist(music_genres, artist_entry)
                    db.session.add(artist_entry)
                    db.session.commit()
                    artist_id = Artist.query.filter_by(name=artist_name).first().id
                else:
                    artist_id = artist_entry.id
                album_image_url = ultimate_album_image_finder(album_title, artist_name, mbid=mb_id)
                if not album_image_url:
                    continue
                cover_art = save_image_from_external_source(album_image_url)
                print("— no cover art —")
                if not cover_art:
                    continue
                print("+ cover art found +")
                album_entry = Album(artist_id=artist_id,
                                    title=album_title,
                                    mb_id=mb_id,
                                    cover_art=cover_art)
                release_date = mb_get_album_release_date(mb_id)
                if release_date:
                    release_date = parse_release_date(release_date)
                    album_entry.release_date = release_date
                alternative_title = mb_get_album_alternative_name(mb_id)
                if alternative_title:
                    album_entry.alternative_title = alternative_title
                discogs_id = get_album_discogs_id(album_title, artist_name)
                if discogs_id:
                    album_entry.discogs_id = discogs_id
                rating = lastfm_get_album_listeners(album_title, artist_name)
                album_entry.rating = rating if rating else 0
                add_album_color(album_entry, 'static/cover_art_new_batch')
                db.session.add(album_entry)
                db.session.commit()
                print("-" * 5)
    except (IOError, OSError) as e:
        print(e)


update_db_with_new_albums()
