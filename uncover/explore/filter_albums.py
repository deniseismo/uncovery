from datetime import datetime

from sqlalchemy import func

from uncover.helpers.utilities import get_filtered_names_list, get_filtered_artist_names
from uncover.models import Album, Artist, Tag, tags


def explore_filtered_albums(genres: list, time_span: list):
    """
    :param genres: a list of music tags/genres
    :param time_span: a list of a time span range [start_year, end_year]
    :return:
    """
    # default time span variables
    start_year = datetime.strptime("1950", '%Y')
    end_year = datetime.strptime("2021", '%Y')
    if time_span:
        time_span[1] += 1
        start_year = datetime.strptime(str(time_span[0]), '%Y')
        end_year = datetime.strptime(str(time_span[1]), '%Y')

    print(f'time_span: {time_span}, genres: {genres}')
    print(start_year, end_year)

    filter_query = Album.query.join(Artist, Artist.id == Album.artist_id) \
        .join(tags, (tags.c.artist_id == Artist.id)).join(Tag, (Tag.id == tags.c.tag_id)) \
        .filter(Album.release_date >= start_year).filter(Album.release_date <= end_year)

    if genres:
        filter_query = filter_query.filter(Tag.tag_name.in_(genres))

    # randomize sample
    filter_query = filter_query.order_by(func.random()).limit(9)

    album_entries = filter_query.all()
    # build an album info dict
    if not album_entries:
        return None
    album_info = {"info": "", "albums": []}
    for counter, album_entry in enumerate(album_entries):
        album_name = album_entry.title
        an_album_dict = {
            "id": counter,
            "title": album_entry.title,
            "names": [album_entry.title.lower()] + get_filtered_names_list(album_name),
            "image": 'static/cover_art_images/' + album_entry.cover_art + ".png",
            "artist_name": album_entry.artist.name,
            "artist_names": [album_entry.artist.name] + get_filtered_artist_names(album_entry.artist.name),
        }
        if album_entry.release_date:
            an_album_dict['year'] = album_entry.release_date.strftime("%Y")
        # remove duplicates
        an_album_dict['artist_names'] = list(set(an_album_dict["artist_names"]))
        an_album_dict['names'] = list(set(an_album_dict['names']))
        album_info["albums"].append(an_album_dict)
    return album_info
