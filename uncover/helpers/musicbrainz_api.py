import urllib.parse
import requests
import requests_cache
import musicbrainzngs

from uncover.utils import jprint
from uncover.helpers.lastfm_api import get_artist_info

requests_cache.install_cache()

# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("albumguesser", "0.1", "denisseismo@gmail.com")


def get_artists_albums(artist, mbid=None, amount=9):
    """

    :param artist: artist's name
    :param mbid: MusicBrainz id (overrides artist's name if present)
    :param amount: a number of albums
    :return:
    """
    my_filter = "' primarytype:album%20AND%20status:official%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json'"
    filters = "%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json"
    another_filter = "http://musicbrainz.org/ws/2/release-group/?query=arid:381086ea-f511-4aba-bdf9-71c753dc5077%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json"
    if mbid:
        artist_mbid = mbid
    else:
        artist_mbid = get_artist_info(artist)
    if not artist_mbid:
        return None
    url = 'https://musicbrainz.org/ws/2/'
    params = {
        'primarytype': 'album',
        'status': 'official',

    }
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json')
    # in case of an error, return None
    if response.status_code != 200:
        return None
    albums = {release['title']: release['id'] for release in response.json()["release-groups"][:]
              if release['artist-credit'][0]['artist']['id'] == artist_mbid}
    print(f'there are {len(albums)} {artist} albums')
    return albums


# for album, id in get_artists_albums('Arcade Fire').items():
#     print(album, (id))


# def get_album_image(mbid, size='small'):
#     """
#     :param mbid: mbid for an album release on MusicBrainz
#     :param size: small, etc.
#     :return: an album cover location
#     """
#     url = "http://coverartarchive.org/release/" + mbid
#     # print(url)
#     response = requests.get(url)
#     if response.status_code != 200:
#         return None
#     print('___images____')
#     jprint(response.json())
#     print('___images____')
#     image = response.json()['images'][0]['thumbnails']['small']
#     return image


def get_album_image(mbid: str, size='small'):
    """
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    if not mbid:
        return None
    url = "http://coverartarchive.org/release-group/" + mbid
    # print(url)
    response = requests.get(url)
    if response.status_code != 200:
        print('something went wrong!')
        return None
    print('___images____')
    # jprint(response.json())
    print('___images____')
    image = response.json()['images'][0]['thumbnails']['small']
    return image


print(get_album_image('c091b282-aa91-3bc0-9c95-938db1f1f930'))


def get_artists_top_albums_via_mb(artist):
    """

    :param artist: artist's name
    :return: a dict of album pictures {album_title: album_image_url}
    """
    try:
        albums = get_artists_albums(artist).items()
    except AttributeError:
        return None
    albums_ids = list(get_artists_albums(artist).values())
    album_images = [get_album_image(album_id) for album_id in albums_ids
                    if get_album_image(album_id)]
    album_info = {album_title: get_album_image(album_id) for album_title, album_id in albums
                  if get_album_image(album_id)}
    # print(f'images: {album_images}')
    # print(f'album info: {album_info}')
    print(len(album_info))
    return album_info


# for album, album_image in get_artists_top_albums_via_mb('Arcade Fire').items():
#     print(f'{album}, ({album_image})')

# musicbrainzngs browsing implementation:
artist_id = "5441c29d-3602-4898-b1a1-b77fa23b8e50"  # bowie
#
# result = musicbrainzngs.browse_releases(artist=artist_id,
#                                         release_type=["album"],
#                                         release_status=['official'],
#                                         limit=100)
# jprint(result)
# print(len(result['release-list']))

# result = musicbrainzngs.browse_release_groups(artist=artist_id,
#                                         release_type=["album"],
#                                         limit=100)
# jprint(result)
# print(len(result['release-group-list']))
# musicbrainzngs release-groups:
# result = musicbrainzngs.get_artist_by_id(artist_id,
#               includes=["release-groups"], release_type=["album"])
# for release_group in result["artist"]["release-group-list"]:
#     print(f'{release_group["title"]} ({release_group["type"]})')
# jprint(result)

# musicbrainzngs releases:
# result = musicbrainzngs.get_artist_by_id(artist_id,
#                                          includes=["releases"],
#                                          release_type=["album"],
#                                          release_status=['official'])
# jprint(result)
# print(len([album['title'] for album in result['artist']['release-list']]))
# print(set([album['title'] for album in result['artist']['release-list']]))


# print(musicbrainzngs.get_release_group_by_id("5441c29d-3602-4898-b1a1-b77fa23b8e50"))
# print(musicbrainzngs.get_release_group_image_list("5db40351-97ed-36a8-88e2-a21a2603cae1"))
# print(musicbrainzngs.get_image_front('f4678eec-fabf-42a3-bcc5-99d2e243bc11'))
# print(get_artists_albums_pictures('David Bowie'))
# print(lookup_tags("David Bowie"))
# print(get_top_albums('Arcade Fire'))
# print(get_users_top_albums('tomsk-seismo'))
# print("bowie's info: ", get_artist_info('David Bowie'))
# print(get_artists_albums("David Bowie"))
#
