import csv

import requests_cache
from tqdm import tqdm
from uncover import create_app
from uncover import db
from uncover.dev.color_analyzer.fill_db_colors import add_album_color
from uncover.dev.db_utils.manage_image_saving import save_image
from uncover.dev.db_utils.manage_names import get_spotify_artist_name
from uncover.dev.db_utils.manage_release_dates import add_album_release_date
from uncover.dev.db_utils.tags_utils import add_artist_music_genres
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artists_albums
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_artists_albums_images
from uncover.models import Artist, Album

app = create_app()
app.app_context().push()

requests_cache.install_cache()


def update_db_with_new_artists():
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
            artist_spotify_name = get_spotify_artist_name(artist_name)
            if artist_spotify_name:
                if artist_spotify_name != artist_name:
                    artist_entry.spotify_name = artist_spotify_name

            db.session.add(artist_entry)
            db.session.commit()
            artist_id = Artist.query.filter_by(name=artist_name).first().id

            for album in tqdm(artist_albums):
                title = album['title']
                rating = album['rating']
                # spotify_id = spotipy_get_album_id(title, artist_name)
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
                    print(image_url)
                cover_art = save_image(image_url)
                print(cover_art)
                if image_url and cover_art:
                    print("image url and cover art TRUTHY")
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
                    add_album_color(album_entry, 'static/cover_art_new_batch')
                    db.session.add(album_entry)

        db.session.commit()
