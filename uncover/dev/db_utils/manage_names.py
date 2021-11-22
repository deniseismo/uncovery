import json
import time

from flask import current_app
from tqdm import tqdm
from uncover import db
from uncover.models import Artist


def fix_spotify_artist_names():
    with open('arist_spotify_names_.json', 'r', encoding='utf-8') as file:
        artist_names = json.load(file)
    for artist_original, artist_spotify in artist_names.items():
        artist_entry = Artist.query.filter_by(name=artist_original).first()
        if artist_entry:
            if artist_entry.spotify_name != artist_spotify:
                artist_entry.spotify_name = artist_spotify
                print(artist_spotify)
                db.session.commit()


def change_spotify_artist_name(artist_name, spotify_artist_name):
    artist_entry = Artist.query.filter_by(name=artist_name).first()
    if artist_entry:
        print(f'changing spotify name: {artist_name} : {spotify_artist_name}')
        artist_entry.spotify_name = spotify_artist_name
        db.session.commit()


def get_artist_spotify_names():
    all_artists = Artist.query.all()
    artist_dict = {artist.name: artist.spotify_name for artist in all_artists if artist.spotify_name}
    import json
    with open('arist_spotify_names.json', 'w', encoding='utf-8') as f:
        json.dump(artist_dict, f, ensure_ascii=False, indent=4)


def get_spotify_artist_name(artist_name):
    import tekore as tk

    client_id = current_app.config['SPOTIPY_CLIENT_ID']
    client_secret = current_app.config['SPOTIPY_CLIENT_SECRET']

    app_token = tk.request_client_token(client_id, client_secret)
    spotify = tk.Spotify(app_token)

    artists_found, = spotify.search(
        query=artist_name,
        types=('artist',),
        limit=5
    )
    if not artists_found:
        return None
    if not artists_found.items:
        return None
    try:
        artist_name_on_spotify = artists_found.items[0].name
        for artist_found in artists_found.items:
            if artist_found.name.lower() == artist_name.lower():
                artist_name_on_spotify = artist_found.name
                return artist_name_on_spotify
    except (TypeError, IndexError):
        return None
    if not getattr(artists_found, 'from_cache', False):
        time.sleep(0.4)
    return artist_name_on_spotify


def populate_spotify_artist_names():
    all_artists = Artist.query.all()
    for artist in tqdm(all_artists):
        if not artist.spotify_name:
            artist_name = artist.name
            spotify_artist_name = get_spotify_artist_name(artist_name)
            if spotify_artist_name:
                if spotify_artist_name != artist_name:
                    print(f'original name: {artist_name}, spotify name: {spotify_artist_name}')
                    artist.spotify_name = spotify_artist_name
                    db.session.commit()
