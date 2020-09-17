from uncover.helpers.discogs_api import get_album_discogs_id, discogs_get_album_image
from uncover.helpers.lastfm_api import lastfm_get_artist_correct_name
from uncover.helpers.musicbrainz_api import mb_get_album_image, mb_get_artists_albums
from uncover.helpers.spotify_api import spotify_get_album_image
from uncover.helpers.utils import timeit


@timeit
def ultimate_album_image_finder(album_title=None, artist=None, mbid=None):
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param album_title:
    :param artist:
    :param mbid:
    :return:
    """
    album_image = None

    # try getting the image through Spotify's API
    if album_title and artist:
        album_image = spotify_get_album_image(album_title, artist)

    # -- MusicBrainz
    if not album_image:
        if mbid:
            album_image = mb_get_album_image(mbid)
            print('finding through mb')

    # -- Discogs
    if not album_image:
        # find album's discogs id
        discogs_id = get_album_discogs_id(album_title, artist)
        if discogs_id:
            album_image = discogs_get_album_image(discogs_id)
            print('finding through discogs')

    if not album_image:
        # No method helped :(
        return None
    return album_image


@timeit
def get_artists_top_albums_images(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = lastfm_get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
        print(f'the correct name is {correct_name}')
    try:
        # gets album titles
        albums = mb_get_artists_albums(artist)
    except AttributeError:
        return None
    if not albums:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": []}
    for album in list(albums):
        album_image = ultimate_album_image_finder(album_title=album['title'], artist=artist, mbid=album['id'])
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
    print(f'there are {len(album_info["albums"])} albums found with Discogs')
    return album_info
