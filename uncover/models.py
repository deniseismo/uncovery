from uncover import db


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    albums = db.relationship('Album', backref='artist', lazy=True)
    genres = db.relationship('Genres', backref='artist', lazy=True)

    def __repr__(self):
        return f"Artist('{self.name}')"


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    rating = db.Column(db.Integer)
    alternative_title = db.Column(db.String())
    cover_art = db.Column(db.String(), nullable=False)
    mb_id = db.Column(db.Integer)
    discogs_id = db.Column(db.Integer)

    def __repr__(self):
        return f"Album('{self.title}', '{self.cover_art}')"


class Genres(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    genre = db.Column(db.String())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
