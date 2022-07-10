from sqlalchemy import func
from uncover import create_app
from uncover.utilities.name_filtering import get_filtered_names_list
from uncover.models import Album, Artist, tags, Tag

app = create_app()
app.app_context().push()


def explore_filtered_albums(genres: list, time_span: list):
    """
    :param genres: a list of music tags/genres
    :param time_span: a list of a time span range [start_year, end_year]
    :return:
    """
    if not genres and not time_span:
        # no filter used
        return None
    genres = ['underground hip-hop']
    start_year = '1950-01-01'
    end_year = '2020-01-01'
    if time_span:
        start_year = str(time_span[0]) + "-01-01"
        end_year = str(time_span[1]) + "-01-01"

    print(start_year, end_year)

    filter_query = Album.query.join(Artist, Artist.id == Album.artist_id) \
        .join(tags, (tags.c.artist_id == Artist.id)).join(Tag, (Tag.id == tags.c.tag_id)) \
        .filter(Album.release_date >= start_year).filter(Album.release_date <= end_year)

    # if genres:
    #     for genre in genres:
    # filter_query = filter_query.filter((Tag.tag_name == "electronic") | (Tag.tag_name == "jazz"))
    filter_query = filter_query.filter(Tag.tag_name.in_(genres))
    print(filter_query.all())
    print(len(filter_query.all()))

    # randomize sample
    filter_query = filter_query.order_by(func.random()).limit(9)

    album_entries = filter_query.all()
    first_album = filter_query.first()
    print(first_album.artist.name)
    # build an album info dict

    album_info = {"info": f"Albums from {start_year} to {end_year}, {genres}", "albums": []}
    counter = 0
    for album_entry in album_entries:
        album_name = album_entry.title
        an_album_dict = {
            "id": counter,
            "title": album_entry.title,
            "names": [album_entry.title.lower()] + get_filtered_names_list(album_name),
            "image": album_entry.cover_art,
            "artist_name": album_entry.artist.name
        }
        album_info["albums"].append(an_album_dict)
        counter += 1
    return album_info


def get_artist_albums_from_db(artist_name):
    artist_entry = Artist.query.filter(Artist.name == artist_name).first()
    artist_albums = artist_entry.albums
    albums = [(album.title, album.mb_id) for album in artist_albums]
    albums.sort()
    for album in albums:
        print(*album)


def find_artists_without_albums():
    all_artists = Artist.query.all()
    artists_without_albums = [artist.name for artist in all_artists if not artist.albums]
    print(len(artists_without_albums))
    for artist_name in artists_without_albums:
        print(artist_name)


get_artist_albums_from_db("Mike Shinoda")