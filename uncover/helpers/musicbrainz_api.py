import requests
import requests_cache
import musicbrainzngs

from uncover.helpers.utils import jprint
from uncover.helpers.lastfm_api import get_artist_info, get_artist_correct_name

requests_cache.install_cache()

# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("albumguesser", "0.1", "denisseismo@gmail.com")


def get_artist_mbid(artist: str):
    """
    search for an artist's mbid on MusicBrainz
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": "artist:" + artist, "limit": "1", "fmt": "json"}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["artists"][0]["id"]
    except (KeyError, IndexError):
        return None
    return mbid


print(get_artist_mbid('Wu-Tang Clan'))


def get_artists_albums_v2(artist: str):
    """
    reserve function in case of some failures
    gets artist's albums by getting mbid directly through MusicBrainz
    (in case there was some error with mbid taken via lastfm)
    :param artist:
    :return:
    """
    artist_mbid = get_artist_mbid(artist)
    if not artist_mbid:
        return None
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json')
    if response.status_code != 200:
        return None
    jprint(response.json())
    albums = {release['title']: release['id'] for release in response.json()["release-groups"][:]
              if release['artist-credit'][0]['artist']['id'] == artist_mbid}
    return albums


def get_artists_albums(artist: str, mbid=None, amount=9):
    """
    :param artist: artist's name
    :param mbid: MusicBrainz id (overrides artist's name if present)
    :param amount: a number of albums
    :return:
    """
    # my_filter = "' primarytype:album%20AND%20status:official%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json'"
    # filters = "%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json"
    # another_filter = "http://musicbrainz.org/ws/2/release-group/?query=arid:381086ea-f511-4aba-bdf9-71c753dc5077%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json"
    if mbid:
        # if mbid is already provided
        artist_mbid = mbid
    else:
        # find mbid through lastfm's API
        artist_mbid = get_artist_info(artist)
    if not artist_mbid:
        # in case lastfm doesn't have an mbid, try finding it directly through MusicBrainz
        artist_mbid = get_artist_mbid(artist)
    if not artist_mbid:
        # if nothing found
        print("could't find correct mbid")
        return None

    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json')
    # in case of an error, return None
    if response.status_code != 200:
        return None
    jprint(response.json())
    albums = {release['title']: release['id'] for release in response.json()["release-groups"][:]
              if release['artist-credit'][0]['artist']['id'] == artist_mbid}
    print(f'there are {len(albums)} {artist} albums')
    if not albums:
        #  in case of some weird error with the mbid taken via lastfm make another attempt with v2
        albums = get_artists_albums_v2(artist)
    return albums


def get_album_image_via_mb(mbid: str, size='large'):
    """
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    if not mbid:
        return None
    url = "http://coverartarchive.org/release-group/" + mbid
    response = requests.get(url)
    if response.status_code != 200:
        print('something went wrong!')
        return None
    jprint(response.json())
    image = response.json()['images'][0]['thumbnails'][size]
    return image


def get_artists_top_albums_via_mb(artist):
    """
    :param artist: artist's name
    :return: a dict of album pictures {album_title: album_image_url}
    """
    # try correcting some typos in artist's name
    correct_name = get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
    try:
        albums = get_artists_albums(artist).items()
    except AttributeError:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": dict()}
    for album_title, album_id in albums:
        if get_album_image_via_mb(album_id):
            album_info["albums"][album_title] = get_album_image_via_mb(album_id)
    print(f'there are {len(album_info["albums"])} cover art images!')
    if not album_info["albums"]:
        # if the artist somehow has no albums to show
        print('error: no albums to show')
        return None
    return album_info
