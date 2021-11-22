from tekore.model import FullTrack

from uncover.utilities.name_filtering import get_filtered_name, remove_punctuation, get_filtered_names_list


def extract_albums_from_user_top_spotify_tracks(track_items: list[FullTrack]):
    """
    :param track_items: a list of FullTrack items (a tekore Track object)
    :return:
    """
    albums = []
    list_of_titles = set()
    for track in track_items:
        if track.album.album_type == 'album':
            name = track.album.name
            filtered_title = get_filtered_name(name)
            filtered_title = remove_punctuation(filtered_title)
            artist_name = track.artists[0].name
            an_album_dict = {
                "artist_name": artist_name,
                "artist_names": [artist_name] + get_filtered_names_list(artist_name),
                "title": name,
                "names": [name.lower()] + get_filtered_names_list(name),
                "image": track.album.images[0].url,
                "rating": track.popularity,
                "spotify_id": track.album.id,
                "year": track.album.release_date[:4]
            }
            an_album_dict["artist_names"] = list(set(an_album_dict["artist_names"]))
            an_album_dict['names'] = list(set(an_album_dict['names']))
            # filter duplicates:
            if filtered_title not in list_of_titles:
                # append a title to a set of titles
                list_of_titles.add(filtered_title)
                # adds an album info only if a title hasn't been seen before
                albums.append(an_album_dict)
    if not albums:
        return None
    return albums
