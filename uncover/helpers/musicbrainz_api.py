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


def get_artists_albums(artist):
    filters = "%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json"
    artist_mbid = get_artist_info(artist)
    # payload = {'query': 'arid:' + artist_mbid}
    # response = requests.get(
    #     url="https://musicbrainz.org/ws/2/",
    #     params=payload
    # )
    # print(artist_mbid)
    url = 'https://musicbrainz.org/ws/2/'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:' + artist_mbid + ' primarytype:album%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json')
    # print(response.json())
    albums = {release['title']: release['releases'][0]['id'] for release in response.json()["release-groups"][:9]}
    # print(f'albums: {albums}')
    return albums


def get_album_image(mbid, size='small'):
    """
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    url = "http://coverartarchive.org/release/" + mbid
    # print(url)
    response = requests.get(url)
    if response.status_code != 200:
        return None
    image = response.json()['images'][0]['thumbnails']['small']
    return image


def get_artists_albums_pictures(artist):
    albums = get_artists_albums(artist).items()
    albums_ids = list(get_artists_albums(artist).values())
    # print(f'ids: {albums_ids}')
    album_images = [get_album_image(album_id) for album_id in albums_ids if get_album_image(album_id)]
    album_info = {album_title: get_album_image(album_id) for album_title, album_id in albums if
                  get_album_image(album_id)}
    # print(f'images: {album_images}')
    # print(f'album info: {album_info}')
    return album_info


artist_id = "5441c29d-3602-4898-b1a1-b77fa23b8e50"  # bowie

result = musicbrainzngs.browse_releases(artist=artist_id, release_type=["album"])
jprint(result)

# result = musicbrainzngs.get_artist_by_id(artist_id,
#               includes=["release-groups"], release_type=["album"])
# for release_group in result["artist"]["release-group-list"]:
#     print("{title} ({type})".format(title=release_group["title"],
#                                     type=release_group["type"]))
# jprint(result)


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

# print(get_artists_albums('David Bowie'))
# print(requests.get('http://coverartarchive.org/release/c04730ea-87cb-478b-a256-08c0561d20e6/').json()['images'][0]['thumbnails']['small'])

# print(requests.get('https://musicbrainz.org//ws/2/release-group?artist=410c9baf-5469-44f6-9852-826524b80c61&type'])=album|ep'))
# print(requests.get('https://musicbrainz.org/ws/2/release-group?query=arid:5441c29d-3602-4898-b1a1-b77fa23b8e50%20primarytype:album%20NOT%20secondarytype:live%20NOT%20secondarytype:compilation%20NOT%20secondarytype:remix%20NOT%20secondarytype:interview%20NOT%20secondarytype:soundtrack&fmt=json').json()['release-groups']
