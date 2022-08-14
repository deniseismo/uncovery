from typing import Optional

from tqdm import tqdm

from uncover import db, create_app
from uncover.dev.update_database.music_genres.music_genres_utils import get_artists_having_fewer_than_n_music_genres, \
    fix_hip_hop_in_music_genres_set, remove_music_genres_with_bad_words_in_them
from uncover.models import Artist, Tag
from uncover.music_apis.lastfm_api.lastfm_music_genres import lastfm_get_artist_music_genres
from uncover.music_apis.spotify_api.spotify_artist_handlers import get_spotify_artist_info, spotify_get_artists_genres
from uncover.utilities.logging_handlers import log_arbitrary_data

app = create_app()
app.config['SERVER_NAME'] = 'localhost'
app.app_context().push()


def populate_music_genres(
        artist_start_id: int = 0,
        sources: tuple = ("spotify", "lastfm"),
        artists_with_few_music_genres: bool = False,
        fewer_than_n_genres: int = 4,
        strictly_all_sources: bool = True,
) -> None:
    """
    add ALL music genres to ALL artists
    :param artist_start_id: (int) artist id in db to start from
    :param sources: (tuple) possible music genre sources: spotify, lastfm
    :param artists_with_few_music_genres: (bool) pick only artists with few music genres
    :param fewer_than_n_genres: (int) pick artists with fewer than N genres (strict < N);
        works only with artists_with_few_music_genres set to True
    :param strictly_all_sources: (bool) take genres from _both_ sources or none at all
    """
    if artists_with_few_music_genres:
        all_artists = get_artists_having_fewer_than_n_music_genres(
            artist_start_id=artist_start_id,
            number_of_music_genres=fewer_than_n_genres
        )
    else:
        all_artists = Artist.query.filter(Artist.id > artist_start_id).all()
    for artist_entry in tqdm(all_artists):
        artist_name = artist_entry.name
        print(f"{artist_name}, {artist_entry.id}")
        music_genres = collect_all_music_genres_for_artist(
            artist_name,
            sources=sources,
            prioritize_spotify=True,
            strictly_all_sources=strictly_all_sources
        )
        if not music_genres:
            print(f"no music genres found for Artist({artist_name})")
            log_arbitrary_data(f"{artist_entry.id}, Artist({artist_name})", "artists_with_no_music_genres.csv")
            continue
        print(*music_genres, sep=", ")
        add_music_genres_to_artist(music_genres, artist_entry)
        print("-" * 8)

    db.session.commit()


def add_music_genres_to_artist(music_genres: set[str], artist_entry: Artist) -> None:
    """
    add music genres to artist; creates new Tag (music genre) if it doesn't exist yet
    :param music_genres: (list[str]) a list of music genre names
    :param artist_entry: (Artist) artist in db
    """
    for tag in music_genres:
        if tag in artist_entry.music_genres:
            print(f"{artist_entry.name} already got Tag({tag}) in their tags")
            continue
        tag_entry = Tag.query.filter_by(tag_name=tag).first()
        if not tag_entry:
            # create new Tag
            tag_entry = Tag(tag_name=tag)
            db.session.add(tag_entry)
            db.session.commit()
        # append artist to the tag, thus creating the many-to-many association between tags & artists
        tag_entry.artists.append(artist_entry)
        db.session.commit()


def collect_all_music_genres_for_artist(
        artist_name: str,
        sources: tuple = ("spotify", "lastfm"),
        prioritize_spotify: bool = True,
        strictly_all_sources: bool = False
) -> Optional[set]:
    """
    get music genres from both Spotify & Last.fm
    :param artist_name:
    :param sources:
    :param prioritize_spotify:
    :param strictly_all_sources: if True, both Spotify & lastfm should return some music genres
    :return:
    """
    print(f"sources picked: {sources}")
    music_genres = set()

    music_genres_storage = {
        "spotify": [],
        "lastfm": []
    }

    artist_spotify_entry = get_spotify_artist_info(artist_name)
    if artist_spotify_entry:
        music_genres_from_spotify = spotify_get_artists_genres(artist_spotify_entry)
        if music_genres_from_spotify:
            a_set_of_music_genres_from_spotify = set(music_genres_from_spotify)
            a_set_of_music_genres_from_spotify = fix_hip_hop_in_music_genres_set(a_set_of_music_genres_from_spotify)
            a_set_of_music_genres_from_spotify = remove_music_genres_with_bad_words_in_them(
                a_set_of_music_genres_from_spotify)
            if prioritize_spotify:
                return a_set_of_music_genres_from_spotify
            music_genres_storage["spotify"] = music_genres_from_spotify
            print(f"from spotify: {music_genres_from_spotify}")
        elif strictly_all_sources:
            return None
    elif strictly_all_sources:
        return None

    music_genres_from_lastfm = lastfm_get_artist_music_genres(artist_name)
    if music_genres_from_lastfm:
        print(f"from lastfm: {music_genres_from_lastfm}")
        a_set_of_music_genres_from_lastfm = set(music_genres_from_lastfm)
        a_set_of_music_genres_from_lastfm = fix_hip_hop_in_music_genres_set(a_set_of_music_genres_from_lastfm)
        a_set_of_music_genres_from_lastfm = remove_music_genres_with_bad_words_in_them(
            a_set_of_music_genres_from_lastfm)
        music_genres_storage["lastfm"] = a_set_of_music_genres_from_lastfm
    elif strictly_all_sources:
        return None

    for source in sources:
        music_genres.update(music_genres_storage[source])

    return music_genres
