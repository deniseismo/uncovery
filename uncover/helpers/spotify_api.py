from uncover.helpers.utils import jprint
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

broken_id = '315gUI'
silk_id = '0IbSjzFvVSG4muNKRoeoJ6'


playlist_tracks = spotify.playlist_tracks(silk_id)
# for track in playlist_tracks["items"]:
#     print(track["track"]["album"]["name"], track["track"]["album"]["images"][0]["url"])


# print(json.dumps(playlist_tracks, sort_keys=True, indent=4))
# album_info = dict()
# playlist_info = spotify.playlist(silk_id)
# # album_info["info"] = f"{playlist_info['name']} by {playlist_info['owner']['display_name']}"
# # print(album_info["info"])
# for track in playlist_info["tracks"]["items"]:
#
# print(json.dumps(playlist_info, sort_keys=True, indent=4))


def get_albums_by_playlist(playlist_id: str):
    """

    :param playlist_id: spotify's playlist ID or a playlist's URL
    :return: a dict {album_title: album_image_url}
    """
    try:
        playlist_tracks = spotify.playlist_tracks(playlist_id)
    except spotipy.exceptions.SpotifyException:
        # Invalid playlist Id
        return None
    # iterate through each track's info object
    album_images = {
        # creates a dict {album_title: album_image_url}
        track["track"]["album"]["name"]: track["track"]["album"]["images"][0]["url"] for track in
        playlist_tracks["items"]
    }
    return album_images

