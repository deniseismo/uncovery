from collections import Counter
from typing import Optional

from tekore._model import FullTrack, PlaylistTrack

from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.schemas.album import AlbumInfo
from uncover.utilities.name_filtering import get_filtered_name, remove_punctuation, get_filtered_names_list


def extract_albums_from_spotify_tracks(
        track_items: list[FullTrack],
        ordered=False
) -> Optional[list[AlbumInfo]]:
    """
    :param track_items: a list of FullTrack items (a tekore Track object)
    :param ordered: ordered by the number of occurrences of an album in a playlist
    :return:
    """
    albums = []
    list_of_titles = set()
    albums_counter = Counter()
    for track in track_items:
        if isinstance(track, PlaylistTrack):
            track = track.track
        elif track.album.album_type != "album":
            continue
        name = track.album.name
        filtered_title = get_filtered_name(name)
        filtered_title = remove_punctuation(filtered_title)
        # filter duplicates:
        if ordered:
            albums_counter[filtered_title] += 1
        if filtered_title in list_of_titles:
            continue
        artist_name = track.artists[0].name
        album_info = AlbumInfo(
            artist_name=artist_name,
            artist_names=[artist_name] + get_filtered_names_list(artist_name),
            title=name,
            names=[name.lower()] + get_filtered_names_list(name),
            image=track.album.images[0].url,
            rating=track.popularity,
            spotify_id=track.album.id,
            year=track.album.release_date[:4]
        )
        album_info.artist_names = list(set(album_info.artist_names))
        album_info.names = list(set(album_info.names))
        # append a title to a set of titles
        list_of_titles.add(filtered_title)
        # adds an album info only if a title hasn't been seen before
        if ordered:
            album_info.filtered_title = filtered_title
        albums.append(album_info)
    if ordered:
        print(albums_counter, len(albums_counter))
        return sorted(albums, key=lambda x: albums_counter[x.filtered_title], reverse=True)
    return albums


def extract_genres_from_spotify_tracks(track_items: list[FullTrack]) -> Counter:
    """
    get a Counter of music genres (a sorted dict of music genre counts in a playlist)
    :param track_items: a list of FullTrack items (a tekore Track object)
    :return: a Counter of music genres (a sorted dict of music genre counts in a playlist)
    """
    spotify_tekore_client = get_spotify_tekore_client()
    genres_counter = Counter()
    for track in track_items:
        if isinstance(track, PlaylistTrack):
            track = track.track
        artist_id = track.artists[0].id
        artist = spotify_tekore_client.artist(artist_id)
        artist_genres = artist.genres
        genres_counter.update(artist_genres)

    return genres_counter