import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())


def get_albums_by_playlist(playlist_id: str):
    """
    :param playlist_id: spotify's playlist ID or a playlist's URL
    :return: a dict {album_title: album_image_url}
    """
    try:
        playlist_info = spotify.playlist(playlist_id)
    except spotipy.exceptions.SpotifyException:
        # Invalid playlist ID
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": f"'{playlist_info['name']}' by {playlist_info['owner']['display_name']}", "albums": dict()}
    # iterate through tracks
    for track in playlist_info["tracks"]["items"]:
        album_info["albums"][track["track"]["album"]["name"]] = track["track"]["album"]["images"][0]["url"]

    return album_info
