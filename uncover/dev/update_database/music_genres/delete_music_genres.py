from uncover import db
from uncover.models import Artist, Tag


def delete_all_music_genres() -> None:
    """
    DANGEROUS! DELETES ALL MUSIC GENRES
    """
    all_artists = Artist.query.all()
    for artist_entry in all_artists:
        remove_music_genres_from_artist(artist_entry)
    all_music_genres = Tag.query.all()
    for genre in all_music_genres:
        db.session.delete(genre)

    db.session.commit()


def remove_music_genres_from_artist(artist_entry: Artist) -> None:
    """
    remove all music genres from artist in db;
    removes genre itself if genre has no artists left
    :param artist_entry: (Artist) object in db
    """
    artist_genres = artist_entry.music_genres

    for genre in list(artist_genres):
        print(f"removing Tag{genre} from Artist({artist_entry.name})")
        artist_entry.music_genres.remove(genre)
        genre.artists.remove(artist_entry)
        db.session.commit()
        if not genre.artists:
            print(f"Tag{genre} has no artists; removing the tag...")
            db.session.delete(genre)
            db.session.commit()
