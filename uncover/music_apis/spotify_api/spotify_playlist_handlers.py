from collections import Counter

from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.album_processing.process_albums_from_spotify import extract_albums_from_spotify_tracks, \
    extract_genres_from_spotify_tracks
from uncover.schemas.album_schema import AlbumInfo


def spotify_get_playlist_albums_by_playlist_id(playlist_id: str) -> list[AlbumInfo]:
    """
    get albums from playlist songs by playlist id
    :param playlist_id: playlist spotify id
    :return: a list of AlbumInfo albums
    """
    spotify_tekore_client = get_spotify_tekore_client()
    playlist = spotify_tekore_client.playlist(playlist_id)
    playlist_tracks = playlist.tracks.items
    playlist_albums = extract_albums_from_spotify_tracks(playlist_tracks, ordered=True)
    return playlist_albums


def spotify_get_genres_from_playlist(playlist_id: str) -> Counter:
    """
    get all music genres with the amount of their occurrences in a playlist
    :param playlist_id: playlist spotify id
    :return: a Counter of music genres
    """
    spotify_tekore_client = get_spotify_tekore_client()
    playlist = spotify_tekore_client.playlist(playlist_id)
    playlist_tracks = playlist.tracks.items
    playlist_genres = extract_genres_from_spotify_tracks(playlist_tracks)
    return playlist_genres
