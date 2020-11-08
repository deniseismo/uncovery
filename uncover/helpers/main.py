from fuzzywuzzy import fuzz
from sqlalchemy import func

import uncover.helpers.discogs_api as discogs_api
import uncover.helpers.lastfm_api as lastfm
import uncover.helpers.musicbrainz_api as musicbrainz
import uncover.helpers.spotify_api as spotify
import uncover.helpers.utilities as utils
from uncover import cache
from uncover.models import Artist, Album


@utils.timeit
@cache.memoize(timeout=360)
def ultimate_album_image_finder(album_title: str, artist: str, mbid=None, fast=False, ultrafast=False):
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param fast: a faster way to get the image (through Spotify first)
    :param mbid: MusicBrainz id of an album
    :param album_title: album's title
    :param artist: artist's name
    :return:
    """
    album_image = None
    # -- MusicBrainz
    if fast:
        album_image = spotify.spotify_get_album_image(album_title, artist)
    if ultrafast:
        return album_image
    if not mbid and fast and not album_image:
        print(f'getting through musicbrainz with no mbid for {album_title}')
        mbid = musicbrainz.mb_get_album_mbid(album_title, artist)
        album_image = musicbrainz.mb_get_album_image(mbid, fast=fast)
    if not mbid and not fast:
        mbid = musicbrainz.mb_get_album_mbid(album_title, artist)
    if mbid and not album_image:
        print('getting through musicbrainz')
        album_image = musicbrainz.mb_get_album_image(mbid, fast=fast)

    if not album_image and not fast:
        # try getting the image through Spotify's API
        album_image = spotify.spotify_get_album_image(album_title, artist)

    # -- Discogs
    if not album_image:
        print(f'getting through discogs for {album_title}')
        # find album's discogs id
        discogs_id = discogs_api.get_album_discogs_id(album_title, artist)
        if discogs_id:
            album_image = discogs_api.discogs_get_album_image(discogs_id)

    if not album_image:
        # No method helped :(
        return None
    return album_image


@utils.timeit
def get_artists_top_albums_images(artist: str, sorting):
    """
    get artist's top album images (default way), no database
    :param artist: artist's name
    :return: a dict of all the album images found
    """
    # try correcting some typos in artist's name
    correct_name = lastfm.lastfm_get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
        print(f'the correct name is {correct_name}')
    try:
        # gets album titles
        # albums = asyncio.run(mb_get_artists_albums(artist, sorting))
        albums = musicbrainz.mb_get_artists_albums(artist, sorting)
        print(type(albums))
        print(albums)
    except AttributeError:
        return None
    if not albums:
        try:
            albums = spotify.spotify_get_artists_albums_images(artist, sorting)
            if albums:
                utils.log_artist_missing_from_db(artist_name=artist)
                return albums
            else:
                return None
        except TypeError:
            return None
    # initialize a dict to avoid KeyErrors
    album_info = {
        "info": {
            "type": "artist",
            "query": artist
        },
        "albums": []
    }
    for album in list(albums):
        album_image = ultimate_album_image_finder(album_title=album['title'],
                                                  artist=artist,
                                                  mbid=album['mbid'],
                                                  fast=True)
        if album_image:
            album['image'] = album_image

    for count, album in enumerate(albums):
        if 'image' in album:
            album['id'] = count
            album_info['albums'].append(album)
    if not album_info['albums']:
        print('error: no albums to show')
        return None
    print(f'there are {len(album_info["albums"])} album images found with the Ultimate')
    if album_info['albums']:
        print(f'search through APIs was successful')
        utils.log_artist_missing_from_db(artist_name=artist)
    return album_info


@cache.memoize(timeout=3600)
def sql_select_artist_albums(artist_name: str, sorting: str):
    """
    search the artist through the database
    :param sorting: sorted by: popularity, release date, randomly
    :param artist_name: artist's name
    :return: album info dict with all the info about albums
    """
    ORDER = {
        "popular": Album.rating.desc(),
        "shuffle": func.random(),
        "latest": Album.release_date.desc(),
        "earliest": Album.release_date.asc()
    }
    ALBUM_LIMIT = 9
    correct_name = lastfm.lastfm_get_artist_correct_name(artist_name)
    if correct_name:
        # corrects the name if there is need
        artist_name = correct_name
    # query artist
    artist = Artist.query.filter_by(name=artist_name).first()
    if not artist:
        # no such artist found
        return None

    # album entries, each of 'Album' SQL class
    album_entries = Album.query.filter_by(artist=artist).order_by(ORDER[sorting]).limit(ALBUM_LIMIT).all()

    # initialize the album info dict
    album_info = {
        "info":
            {
                "type": "artist",
                "query": artist_name
            },
        "albums": []
    }
    for count, album in enumerate(album_entries):
        an_album_dict = {
            "title": album.title,
            "names": [album.title.lower()] + utils.get_filtered_names_list(album.title),
            "id": count,
            "rating": album.rating,
            "image": 'static/cover_art_images/' + album.cover_art + ".png"
        }
        if album.release_date:
            an_album_dict['year'] = album.release_date
        if album.alternative_title:
            an_album_dict['names'] += [album.alternative_title]
            an_album_dict["names"] += utils.get_filtered_names_list(album.alternative_title)
        an_album_dict['names'] = list(set(an_album_dict['names']))
        album_info['albums'].append(an_album_dict)
    return album_info


@cache.memoize(timeout=360)
def sql_find_specific_album(artist_name: str, an_album_to_find: str):
    """
    finds a specific album image via database
    :param artist_name: artist's name
    :param an_album_to_find: album's title
    :return:
    """
    artist = Artist.query.filter_by(name=artist_name).first()
    print(f'artist found in sql: {artist}')
    if not artist:
        # no such artist found
        print('no artist found')
        # logs an artist to the missing artists list log
        utils.log_artist_missing_from_db(artist_name=artist_name)
        return None
    print('artist found')
    album_entries = Album.query.filter_by(artist=artist).all()
    album_found = None
    ratio_threshold = 94
    an_album_to_find = an_album_to_find.lower()
    for album in album_entries:
        album_title = album.title.lower()
        print(album.title, an_album_to_find)
        # implements a fuzzy match algorithm function
        current_ratio = fuzz.ratio(album_title, an_album_to_find)
        partial_ratio = fuzz.partial_ratio(album_title, an_album_to_find)
        if partial_ratio == 100:
            album_found = album.cover_art
        if current_ratio > 98:
            # found perfect match, return immediately
            return 'static/cover_art_images/' + album.cover_art + ".png"
        elif current_ratio > ratio_threshold:
            ratio_threshold = current_ratio
            album_found = album.cover_art
    if not album_found:
        return None
    return 'static/cover_art_images/' + album_found + ".png"
