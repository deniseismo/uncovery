import asyncio
from typing import Optional

from asyncio import Future

from uncover import cache
from uncover.music_apis.discogs_api.discogs_album_handlers import get_album_discogs_id, discogs_get_album_image
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_mbid, mb_get_album_image
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_album_image
from uncover.schemas.album_schema import AlbumInfo


@cache.memoize(timeout=360)
def ultimate_album_image_finder(
        album_title: str,
        artist: str,
        mbid: str = None,
        fast: bool = False,
        ultrafast: bool = False
) -> Optional[str]:
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param album_title: album's title
    :param artist: artist's name
    :param mbid: MusicBrainz id of an album
    :param fast: a faster way to get the image (through Spotify first)
    :param ultrafast: return image right away;
    after trying to get it the fast way (through spotify) even if no image was found this way
    :return: (str) album image url
    """
    if not album_title or not artist:
        return None
    album_image = None

    if fast:
        album_image = spotify_get_album_image(album_title, artist)
    if ultrafast:
        return album_image
    if not mbid and fast and not album_image:
        print(f'getting through musicbrainz with no mbid for {album_title}')
        mbid = mb_get_album_mbid(album_title, artist)
        album_image = mb_get_album_image(mbid, fast=fast)
    if not mbid and not fast:
        mbid = mb_get_album_mbid(album_title, artist)
    if mbid and not album_image:
        print('getting through musicbrainz')
        album_image = mb_get_album_image(mbid, fast=fast)

    if not album_image and not fast:
        # try getting the image through Spotify's API
        album_image = spotify_get_album_image(album_title, artist)

    # -- Discogs
    if not album_image:
        print(f'getting through discogs for {album_title}')
        # find album's discogs id
        discogs_id = get_album_discogs_id(album_title, artist)
        if discogs_id:
            album_image = discogs_get_album_image(discogs_id)

    if not album_image:
        # No method helped :(
        return None
    return album_image


async def ultimate_album_image_fetcher(
        album_title: str,
        artist: str,
        mbid: str = None,
        fast: bool = False,
        ultrafast: bool = False
) -> Optional[str]:
    """
    try finding an album image through Spotify → MusicBrainz → Discogs
    :param album_title: album's title
    :param artist: artist's name
    :param mbid: MusicBrainz id of an album
    :param fast: a faster way to get the image (through Spotify first)
    :param ultrafast: return image right away;
    after trying to get it the fast way (through spotify) even if no image was found this way
    :return: (str) album image url
    """
    if not album_title or not artist:
        return None
    album_image = None
    # -- MusicBrainz
    if fast:
        album_image = spotify_get_album_image(album_title, artist)
    if ultrafast:
        return album_image
    if not mbid and fast and not album_image:
        print(f'getting through musicbrainz with no mbid for {album_title}')
        mbid = mb_get_album_mbid(album_title, artist)
        album_image = mb_get_album_image(mbid, fast=fast)
    if not mbid and not fast:
        mbid = mb_get_album_mbid(album_title, artist)
    if mbid and not album_image:
        print('getting through musicbrainz')
        album_image = mb_get_album_image(mbid, fast=fast)

    if not album_image and not fast:
        # try getting the image through Spotify's API
        album_image = spotify_get_album_image(album_title, artist)

    # -- Discogs
    if not album_image:
        print(f'getting through discogs for {album_title}')
        # find album's discogs id
        discogs_id = get_album_discogs_id(album_title, artist)
        if discogs_id:
            album_image = discogs_get_album_image(discogs_id)

    if not album_image:
        # No method helped :(
        return None
    return album_image


async def fetch_and_assign_images(albums_list: list[AlbumInfo], artist: str):
    tasks = []
    for album in albums_list:
        task = asyncio.create_task(add_album_image(album, artist))
        tasks.append(task)

    await asyncio.gather(*tasks)


async def add_album_image(album: AlbumInfo, artist: str):
    album_image = await ultimate_album_image_fetcher(album_title=album.title,
                                                     artist=artist,
                                                     mbid=album.mbid,
                                                     fast=True)
    if album_image:
        album.image = album_image
