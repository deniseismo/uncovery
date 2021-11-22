from tqdm import tqdm
from uncover import db
from uncover.music_apis.spotify_api.spotify_album_handlers import spotipy_get_album_id
from uncover.models import Album


def populate_spotify_album_ids():
    all_albums = Album.query.filter(Album.id > 16131).all()
    for album in tqdm(all_albums):
        if album.spotify_id:
            print(f'{album.title} already has spotify id, skipping')
            continue
        artist_name = album.artist.name
        album_name = album.title
        spotify_id = spotipy_get_album_id(album_name, artist_name)
        if spotify_id:
            print(f'adding {artist_name} - {album_name}: {spotify_id}')
            album.spotify_id = spotify_id
            db.session.commit()

    db.session.commit()
