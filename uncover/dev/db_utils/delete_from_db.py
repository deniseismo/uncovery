from uncover import create_app, db
from uncover.models import Album, Artist

app = create_app()
app.app_context().push()


def delete_particular_artist_and_albums_from_db(artist_name):
    """
    BE CAREFUL!
    deletes all artist's albums and the artist as well
    :param artist_name: artist to delete from db
    :return: None
    """
    artist_entry = Artist.query.filter_by(name=artist_name).first()
    if artist_entry:
        print(f'...deleting {artist_name}')
        for album in artist_entry.albums:
            db.session.delete(album)
        db.session.delete(artist_entry)
        db.session.commit()


def delete_particular_album(album_name: str, artist_name=None):
    """
    BE CAREFUL! deletes the first appearance of an album with the given title
    :param artist_name: artist's name
    :param album_name: album's name
    :return:
    """
    album_entries = Album.query.filter_by(title=album_name).all()
    if not album_entries:
        print('no album found')
        return False
    if album_entries:
        if not artist_name:
            album_to_delete = album_entries[0]
        else:
            for album in album_entries:
                if album.artist.name == artist_name:
                    album_to_delete = album

        if album_to_delete:
            print(f'deleting {album_to_delete} by {album_to_delete.artist.name}')
            db.session.delete(album_to_delete)
            db.session.commit()


def delete_album_by_album_id(album_db_id: int):
    """BE CAREFUL!
    deletes a particular album (given album db id) and all the songs from this album

    Args:
        album_db_id (int): album id (id in database)
    """
    album_to_delete = Album.query.get(album_db_id)
    if album_to_delete:
        print(f"deleting: Album({album_to_delete.title}) by ({album_to_delete.artist.name})")
    db.session.delete(album_to_delete)
    db.session.commit()

# delete_album_by_album_id(52427)
