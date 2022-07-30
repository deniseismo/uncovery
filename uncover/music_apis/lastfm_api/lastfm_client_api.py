import asyncio
from typing import Optional

import aiohttp
import requests
from flask import current_app


def lastfm_get_response(payload: dict) -> Optional[requests.Response]:
    """
    get a response from lastfm given some payload info
    :param payload: user's request information: method and other lastfm api specific params
    :return: requests.Response
    """
    # define headers and URL
    headers = {'user-agent': current_app.config['USER_AGENT']}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = current_app.config['API_KEY']
    payload['format'] = 'json'
    try:
        response = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return None
    return response


async def lastfm_fetch_response(payload: dict, session: aiohttp.ClientSession):
    """
    get a response from lastfm given some payload info (async)
    :param payload:
    :param session: aiohttp.ClientSession
    :return:
    """
    # define headers and URL
    headers = {'user-agent': current_app.config['USER_AGENT']}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = current_app.config['API_KEY']
    payload['format'] = 'json'
    async with session.get(url, headers=headers, params=payload) as response:
        if response.status != 200:
            return None
        if not getattr(response, 'from_cache', False):
            await asyncio.sleep(0.2)
        return await response.json()
