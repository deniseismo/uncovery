import uncover.helpers.discogs_api as discogs_api
import uncover.helpers.lastfm_api as lastfm_api
from uncover.helpers.musicbrainz_api import mb_get_album_image, mb_get_artists_albums, mb_get_album_mbid
from uncover.helpers.spotify_api import spotify_get_album_image
from uncover.helpers.utils import timeit, get_filtered_names_list
from uncover.models import Artist, Album


@timeit
def ultimate_album_image_finder(album_title: str, artist: str, mbid=None):
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param mbid: MusicBrainz id of an album
    :param album_title: album's title
    :param artist: artist's name
    :return:
    """
    album_image = None
    # -- MusicBrainz
    if not mbid:
        mbid = mb_get_album_mbid(album_title, artist)
    if mbid:
        print(f'mbid: {mbid}, album: {album_title}')
        album_image = mb_get_album_image(mbid)
        print('finding through mb')

    if not album_image:
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


@timeit
def get_artists_top_albums_images(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = lastfm_api.lastfm_get_artist_correct_name(artist)
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
    print(f'there are {len(album_info["albums"])} album images found with the Ultimate')
    return album_info


def sql_select(artist_name: str):
    correct_name = lastfm_api.lastfm_get_artist_correct_name(artist_name)
    if correct_name:
        artist_name = correct_name
    artist = Artist.query.filter_by(name=artist_name).first()
    if not artist:
        return None
    album_entries = Album.query.filter_by(artist=artist).order_by(Album.rating.desc()).limit(9).all()
    album_id = 0
    album_info = {"info": artist_name, "albums": []}
    for album in album_entries:
        an_album_dict = {
            "title": album.title,
            "names": [album.title.lower()] + get_filtered_names_list(album.title),
            "id": album_id,
            "rating": album.rating,
            "image": 'static/cover_art_images/' + album.cover_art + ".png"
        }
        if album.alternative_title:
            an_album_dict['names'] += album.alternative_title
            an_album_dict["names"] += get_filtered_names_list(album.alternative_title)

        album_info['albums'].append(an_album_dict)
        album_id += 1
    return album_info
