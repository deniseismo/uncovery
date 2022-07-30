from collections import Counter
from typing import Optional

from tekore._model import FullTrack, PlaylistTrack, SimpleAlbum

from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.convert_values import parse_release_date
from uncover.utilities.name_filtering import get_filtered_name, remove_punctuation, get_filtered_names_list


def extract_albums_from_spotify_tracks(track_items: list[FullTrack], ordered=False) -> Optional[list[AlbumInfo]]:
    """
    :param track_items: a list of FullTrack items (a tekore Track object)
    :param ordered: ordered by the number of occurrences of an album in a playlist
    :return: list[AlbumInfo]
    """
    albums = []
    list_of_titles = set()
    albums_counter = Counter()
    for track in track_items:
        if isinstance(track, PlaylistTrack):
            track = track.track
        elif track.album.album_type != "album":
            continue
        album_name = track.album.name
        filtered_title = get_filtered_name(album_name)
        filtered_title = remove_punctuation(filtered_title)
        # filter duplicates:
        if ordered:
            albums_counter[filtered_title] += 1
        if filtered_title in list_of_titles:
            continue
        artist_name = track.artists[0].name
        parsed_release_date = parse_release_date(track.album.release_date)
        album_info = AlbumInfo(
            artist_name=artist_name,
            artist_names=[artist_name] + get_filtered_names_list(artist_name),
            title=album_name,
            names=[album_name.lower()] + get_filtered_names_list(album_name),
            image=track.album.images[0].url,
            rating=track.popularity,
            spotify_id=track.album.id,
            year=parsed_release_date.year
        )
        album_info.remove_duplicate_names()
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


def process_spotify_artist_albums(albums: list[SimpleAlbum]) -> list[AlbumInfo]:
    """
    extract all the needed info from artist's albums found on Spotify
    :param albums: a list of Spotify albums by artist; list[SimpleAlbum]
    :return: list[AlbumInfo]
    """
    a_set_of_titles = set()
    processed_albums = []
    for album in albums:
        album_image = album.images[0].url
        album_title = album.name
        artist_name = album.artists[0].name
        filtered_name = get_filtered_name(album_title)
        if filtered_name not in a_set_of_titles:
            a_set_of_titles.add(filtered_name)
            correct_title = album_title.lower()
            rating = lastfm_get_album_listeners(correct_title, artist_name)
            parsed_release_date = parse_release_date(album.release_date)
            album_info = AlbumInfo(
                title=album_title,
                artist_name=album.artists[0].name,
                image=album_image,
                names=[correct_title] + get_filtered_names_list(album_title),
                rating=rating if rating else 0,
                year=parsed_release_date.year,
                artist_names=[artist_name]
            )
            # remove duplicates
            album_info.remove_duplicate_names()
            processed_albums.append(album_info)
    return processed_albums


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
