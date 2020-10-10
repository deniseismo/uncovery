from fuzzywuzzy import fuzz

import uncover.helpers.discogs_api as discogs_api
import uncover.helpers.lastfm_api as lastfm
import uncover.helpers.musicbrainz_api as musicbrainz
import uncover.helpers.utilities as utils
from uncover.helpers.spotify_api import spotify_get_album_image
from uncover.models import Artist, Album


@utils.timeit
def ultimate_album_image_finder(album_title: str, artist: str, mbid=None, fast=False):
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
        album_image = spotify_get_album_image(album_title, artist)
        print(f'{album_image} through Spotify {album_title}')
    if not mbid and not fast:
        mbid = musicbrainz.mb_get_album_mbid(album_title, artist)
    if mbid and not album_image:
        print(f'mbid: {mbid}, album: {album_title}')
        album_image = musicbrainz.mb_get_album_image(mbid, fast=fast)
        print('finding through mb')

    if not album_image and not fast:
        # try getting the image through Spotify's API
        album_image = spotify_get_album_image(album_title, artist)
        print('finding through spotify')

    # -- Discogs
    if not album_image:
        # find album's discogs id
        discogs_id = discogs_api.get_album_discogs_id(album_title, artist)
        if discogs_id:
            album_image = discogs_api.discogs_get_album_image(discogs_id)
            print(f'finding {album_title} through discogs')

    if not album_image:
        # No method helped :(
        return None
    return album_image


@utils.timeit
def get_artists_top_albums_images(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = lastfm.lastfm_get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
        print(f'the correct name is {correct_name}')
    try:
        # gets album titles
        albums = musicbrainz.mb_get_artists_albums(artist)
    except AttributeError:
        return None
    if not albums:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": []}
    for album in list(albums):
        album_image = ultimate_album_image_finder(album_title=album['title'], artist=artist, mbid=album['id'],
                                                  fast=True)
        if album_image:
            album['image'] = album_image
    album_id = 0
    for album in albums:
        if 'image' in album:
            album['id'] = album_id
            album_info['albums'].append(album)
            album_id += 1
    if not album_info['albums']:
        print('error: no albums to show')
        return None
    print(f'there are {len(album_info["albums"])} album images found with the Ultimate')
    if album_info['albums']:
        print(f'search through APIs was successful')
        utils.log_artist_missing_from_db(artist_name=artist)
    return album_info


def sql_select_artist_albums(artist_name: str):
    """
    search the artist through the database
    :param artist_name:
    :return: album info dict with all the info about albums
    """
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
    album_entries = Album.query.filter_by(artist=artist).order_by(Album.rating.desc()).limit(ALBUM_LIMIT).all()

    album_id = 0
    # initialize the album info dict
    album_info = {"info": artist_name, "albums": []}
    for album in album_entries:
        an_album_dict = {
            "title": album.title,
            "names": [album.title.lower()] + utils.get_filtered_names_list(album.title),
            "id": album_id,
            "rating": album.rating,
            "image": 'static/cover_art_images/' + album.cover_art + ".png"
        }
        if album.alternative_title:
            print(album.alternative_title)

            an_album_dict['names'] += [album.alternative_title]
            an_album_dict["names"] += utils.get_filtered_names_list(album.alternative_title)
        an_album_dict['names'] = list(set(an_album_dict['names']))
        album_info['albums'].append(an_album_dict)
        album_id += 1
    return album_info


def sql_find_specific_album(artist_name: str, an_album_to_find: str):
    artist = Artist.query.filter_by(name=artist_name).first()
    if not artist:
        # no such artist found
        print('no artist found')
        utils.log_artist_missing_from_db(artist_name=artist_name)
        return None
    print('artist found')
    album_entries = Album.query.filter_by(artist=artist).all()
    album_found = None
    ratio_threshold = 94
    for album in album_entries:
        current_ratio = fuzz.ratio(album.title, an_album_to_find)
        if current_ratio > 98:
            # found perfect match
            print(f'{album.title}, {current_ratio}')
            return 'static/cover_art_images/' + album.cover_art + ".png"
        elif current_ratio > ratio_threshold:
            ratio_threshold = current_ratio
            album_found = album.cover_art
    if not album_found:
        return None
    return 'static/cover_art_images/' + album_found + ".png"
