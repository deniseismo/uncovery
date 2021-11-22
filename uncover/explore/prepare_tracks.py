from uncover.utilities.name_filtering import get_filtered_names_list


def process_albums_from_db(album_entries: list):
    """
    process album entries from database
    :param album_entries: a list of album entries from db
    :return: a list of album info dicts
    """
    processed_albums = []
    for counter, album_entry in enumerate(album_entries):
        album_name = album_entry.title
        an_album_dict = {
            "id": counter,
            "title": album_entry.title,
            "names": [album_entry.title.lower()] + get_filtered_names_list(album_name),
            "image": f'static/optimized_cover_art_images/{album_entry.cover_art}.jpg',
            "image_small": f'static/optimized_cover_art_images/{album_entry.cover_art}-size200.jpg',
            "image_medium": f'static/optimized_cover_art_images/{album_entry.cover_art}-size300.jpg',
            "artist_name": album_entry.artist.name,
            "artist_names": [album_entry.artist.name] + get_filtered_names_list(album_entry.artist.name),
        }
        if album_entry.artist.spotify_name:
            an_album_dict['spotify_name'] = album_entry.artist.spotify_name
        if album_entry.release_date:
            an_album_dict['year'] = album_entry.release_date.strftime("%Y")
        if album_entry.alternative_title:
            an_album_dict['names'] += [album_entry.alternative_title]
            an_album_dict["names"] += get_filtered_names_list(album_entry.alternative_title)
        # remove duplicates
        an_album_dict['artist_names'] = list(set(an_album_dict["artist_names"]))
        an_album_dict['names'] = list(set(an_album_dict['names']))
        processed_albums.append(an_album_dict)
    return processed_albums