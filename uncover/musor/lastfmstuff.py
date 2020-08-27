import json
import os
import time

import requests
import requests_cache

requests_cache.install_cache()

# import pandas


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent':  os.environ.get('USER_AGENT')}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = os.environ.get('API_KEY')
    payload['format'] = 'json'
    response = requests.get(url, headers=headers, params=payload)
    return response


# r = lastfm_get_response({
#     'method': 'chart.gettopartists'
# })
#
# # prints top artists names
# # for artist in r.json()['artists']['artist']:
# #     print(artist.get('name'))
#
# # jprint(r.json()['artists']['@attr'])

# page = 1
# total_pages = 99999
# responses = []
#
# while page <= total_pages:
#     payload = {
#         'method': 'chart.gettopartists',
#         'limit': 500,
#         'page': page
#     }
#     # print some output so we can see the status
#     print("Requesting page {}/{}".format(page, total_pages))
#     # clear the output to make things neater
#     clear_output(wait=True)
#
#     # make the API call
#     response = lastfm_get_response(payload)
#
#     # if we get an error, print the response and halt the loop
#     if response.status_code != 200:
#         print(response.text)
#         break
#
#     # extract pagination info
#     page = int(response.json()['artists']['@attr']['page'])
#     total_pages = int(response.json()['artists']['@attr']['totalPages'])
#
#     # append response
#     responses.append(response)
#
#     # if it's not a cached result, sleep
#     if not getattr(response, 'from_cache', False):
#         time.sleep(0.25)
#
#     # increment the page number
#     page += 1
#
#
# frames = [pandas.DataFrame(r.json()['artists']['artist']) for r in responses]
# artists = pandas.concat(frames)
# artists = artists.drop('image', axis=1)
# artists = artists.drop_duplicates().reset_index(drop=True)
# artists.head()
# print('here comes the info')
# print(artists.info())
# print('here comes description')
# print(artists.describe())
# artist_counts = [len(r.json()['artists']['artist']) for r in responses]

def lookup_tags(artist):
    """
    :param artist: musician/band
    :return: top 3 tags from the given artist in the form of a string
    """
    response = lastfm_get({
        'method': 'artist.getTopTags',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    tags = [tag['name'] for tag in response.json()['toptags']['tag'][:3]]

    tags_string = ', '.join(tags)

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return tags_string


print(lookup_tags('David Bowie'))
