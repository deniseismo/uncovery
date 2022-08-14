import time

from tqdm import tqdm

from uncover import db, create_app
from uncover.models import Album
from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners

app = create_app()
app.app_context().push()


def update_album_ratings(album_start_id: int = 0) -> None:
    """
    updates all album ratings
    :param album_start_id: (int) album id in db to start from
    """
    album_count = 0
    all_albums = Album.query.filter(Album.id > album_start_id).all()
    for album_entry in tqdm(all_albums):
        print("-" * 10)
        artist_name = album_entry.artist.name
        print(f"Checking {album_entry}, id({album_entry.id})")
        rating = lastfm_get_album_listeners(album_entry.title, artist_name)
        if not rating:
            continue
        if album_entry.rating != rating:
            print(f"\n--{album_entry}, {album_entry.id} --")
            print(album_entry.rating, "→", rating)
            album_entry.rating = rating
        album_count += 1
        time.sleep(1)
        if album_count % 30 == 0:
            time.sleep(5)

        db.session.commit()
