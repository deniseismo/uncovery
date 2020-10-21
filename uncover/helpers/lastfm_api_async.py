import asyncio
from flask import current_app

import uncover.helpers.utilities as utils


async def lastfm_fetch_response(payload: dict, session):
    # define headers and URL
    headers = {'user-agent': current_app.config['USER_AGENT']}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = current_app.config['API_KEY']
    payload['format'] = 'json'
    async with session.get(url, headers=headers, params=payload) as response:
        if not getattr(response, 'from_cache', False):
            asyncio.sleep(0.2)
        return await response.json()


@utils.timeit
async def lastfm_fetch_album_listeners(album: str, artist: str, session):
    """
    gets the number of listeners of a particular album
    :param album: album's title
    :param artist: artist's name
    :return:
    """
    response = await lastfm_fetch_response({
        'method': ' album.getInfo',
        'album': album,
        'artist': artist
    }, session)
    # in case of an error, return None
    try:
        album_listeners = response['album']['listeners']
    except KeyError:
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)

# async def main():
#     async with aiohttp.ClientSession() as session:
#         listeners = await lastfm_fetch_album_listeners("Hunky Dory", "David Bowie", session=session)
#         return listeners
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     listeners = loop.run_until_complete(main())
#     print(listeners)
