import time

from tqdm import tqdm

from uncover import db, create_app
from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners
from uncover.models import Album

app = create_app()
app.app_context().push()


def double_check_album_rating(album_start_id=0):
    """double check album rating
    """
    album_count = 0
    all_albums = Album.query.filter(Album.id > album_start_id).all()
    for album in tqdm(all_albums):
        print("-" * 10)

        album_title = album.title.lower()
        artist_name = album.artist.name
        print(f"Checking Album({album_title}), id({album.id}) by Artist({artist_name})")
        rating = lastfm_get_album_listeners(album_title, artist_name)
        if not rating:
            continue
        if album.rating != rating:
            print(f"\n--{album_title}, {album.id} by {artist_name}--")
            print(album.rating, "→", rating)
            album.rating = rating
        album_count += 1
        time.sleep(1)
        if album_count % 30 == 0:
            time.sleep(5)
        db.session.commit()


double_check_album_rating(37004)
