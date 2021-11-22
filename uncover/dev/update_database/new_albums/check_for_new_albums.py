import csv

from tqdm import tqdm
from uncover import create_app
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artist_albums_v2
from uncover.models import Artist

app = create_app()
app.app_context().push()


def check_music_brainz_for_new_albums(artist_start_id=0):
    # get all artists from db
    # lana = Artist.query.get(769)
    # avalanches = Artist.query.get(1171)
    # all_artists = [lana, avalanches]
    # beatles = Artist.query.get(2613)
    # all_artists = Artist.query.all()
    # all_artists = [beatles]
    all_artists = Artist.query.filter(Artist.id > artist_start_id).all()
    fieldnames = ["artist", "album_title", "mb_id"]
    with open("new_albums_found.csv", "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        csvfile.writeheader()

    for artist in tqdm(all_artists):
        db_albums = artist.albums
        artist_name = artist.name
        print(artist_name, artist.id)
        albums_from_mb = mb_get_artist_albums_v2(artist_name)
        # albums_from_mb = mb_get_artist_albums_v2(
        #     artist_name,
        #     album_query_filter=' AND primarytype:album AND secondarytype:Soundtrack AND status:official&fmt=json')
        if not albums_from_mb:
            continue
        print(albums_from_mb, len(albums_from_mb))
        if len(albums_from_mb) != len(db_albums):
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


check_music_brainz_for_new_albums()
