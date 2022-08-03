import asyncio
from typing import Optional

from uncover import cache
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id, discogs_get_album_image
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_mbid, mb_get_album_image
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_album_image
from uncover.schemas.album_schema import AlbumInfo


@cache.memoize(timeout=360)
def ultimate_album_image_finder(
        album_title: str,
        artist_name: str,
        mbid: str = None,
        fast: bool = False,
        ultrafast: bool = False
) -> Optional[str]:
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param album_title: album's title
    :param artist_name: artist's name
    :param mbid: MusicBrainz id of an album
    :param fast: a faster way to get the image (through Spotify first)
    :param ultrafast: return image right away;
    after trying to get it the fast way (through spotify) even if no image was found this way
    :return: (str) album image url
    """
    if not album_title or not artist_name:
        return None
    album_image = None

    # spotify is the fastest way
    if fast:
        album_image = spotify_get_album_image(album_title, artist_name)
    # return even if we don't find any image
    if ultrafast:
        return album_image
    # no image found through spotify, no mbid → try finding mbid → get image through musicbrainz
    if not mbid and fast and not album_image:
        mbid = mb_get_album_mbid(album_title, artist_name)
        if mbid:
            album_image = mb_get_album_image(mbid, fast=fast)
    # not fast → we didn't try finding through spotify right away → try getting through musicbrainz first
    if not mbid and not fast:
        mbid = mb_get_album_mbid(album_title, artist_name)
    if mbid and not album_image:
        album_image = mb_get_album_image(mbid, fast=fast)

    if not album_image and not fast:
        # not fast & no image so far → we started with musicbrainz and didn't find anything → try through spotify
        album_image = spotify_get_album_image(album_title, artist_name)

    # discogs is the last resort: the slowest method
    if not album_image:
        discogs_id = get_album_discogs_id(album_title, artist_name)
        if discogs_id:
            album_image = discogs_get_album_image(discogs_id)

    if not album_image:
        # no method helped
        print(f"no image is found for Album({album_title}) by Artist({artist_name})")
        return None
    return album_image


async def ultimate_album_image_fetcher(
        album_title: str,
        artist_name: str,
        mbid: str = None,
        fast: bool = False,
        ultrafast: bool = False
) -> Optional[str]:
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param album_title: album's title
    :param artist_name: artist's name
    :param mbid: MusicBrainz id of an album
    :param fast: a faster way to get the image (through Spotify first)
    :param ultrafast: return image right away;
    after trying to get it the fast way (through spotify) even if no image was found this way
    :return: (str) album image url
    """
    if not album_title or not artist_name:
        return None
    album_image = None

    # spotify is the fastest way
    if fast:
        album_image = spotify_get_album_image(album_title, artist_name)
    # return even if we don't find any image
    if ultrafast:
        return album_image
    # no image found through spotify, no mbid → try finding mbid → get image through musicbrainz
    if not mbid and fast and not album_image:
        mbid = mb_get_album_mbid(album_title, artist_name)
        if mbid:
            album_image = mb_get_album_image(mbid, fast=fast)
    # not fast → we didn't try finding through spotify right away → try getting through musicbrainz first
    if not mbid and not fast:
        mbid = mb_get_album_mbid(album_title, artist_name)
    if mbid and not album_image:
        album_image = mb_get_album_image(mbid, fast=fast)

    if not album_image and not fast:
        # not fast & no image so far → we started with musicbrainz and didn't find anything → try through spotify
        album_image = spotify_get_album_image(album_title, artist_name)

    # discogs is the last resort: the slowest method
    if not album_image:
        discogs_id = get_album_discogs_id(album_title, artist_name)
        if discogs_id:
            album_image = discogs_get_album_image(discogs_id)

    if not album_image:
        # no method helped
        print(f"no image is found for Album({album_title}) by Artist({artist_name})")
        return None
    return album_image


async def fetch_and_assign_images(albums_list: list[AlbumInfo], artist_name: str):
    """
    try getting images for each album (AlbumInfo) async.
    :param albums_list: (list[AlbumInfo]) list of AlbumInfo albums (but without images)
    :param artist_name: (str) artist's name
    """
    tasks = []
    for album_info in albums_list:
        task = asyncio.create_task(add_album_image(album_info, artist_name))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def add_album_image(album_info: AlbumInfo, artist_name: str):
    """
    find album's cover for AlbumInfo
    :param album_info: (AlbumInfo) album info (without images)
    :param artist_name: artist's name
    :return:
    """
    album_image = await ultimate_album_image_fetcher(album_title=album_info.title,
                                                     artist_name=artist_name,
                                                     mbid=album_info.mbid,
                                                     fast=True)
    # add image url if image is found
    if album_image:
        album_info.image = album_image
