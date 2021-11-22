from datetime import datetime

from tqdm import tqdm
from uncover import db
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_release_date
from uncover.models import Album


def populate_release_dates():
    all_albums = Album.query.all()
    for album in tqdm(all_albums):
        if album.release_date:
            continue
        if album.mb_id:
            print(f'trying {album.title}, {album.mb_id}')
            release_date = mb_get_album_release_date(album.mb_id)
            if release_date:
                parsed_release_date = datetime.strptime(release_date[:4], '%Y')
                album.release_date = parsed_release_date
                print(f'adding release date ({parsed_release_date}) to ({album.title})')

    db.session.commit()


def add_album_release_date(album):
    """
    :param album: album entry (Album class)
    :return:
    """
    if album.mb_id:
        print(f'trying {album.title}, {album.mb_id}')
        release_date = mb_get_album_release_date(album.mb_id)
        if release_date:
            parsed_release_date = datetime.strptime(release_date[:4], '%Y')
            album.release_date = parsed_release_date
            print(f'adding release date ({parsed_release_date}) to ({album.title})')
    db.session.commit()
