from uncover import db


tags = db.Table(
    'tags',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, index=True, nullable=False)
    albums = db.relationship('Album', backref='artist', lazy=True)
    music_genres = db.relationship('Tag', secondary=tags,
                                   backref=db.backref('artists', lazy='dynamic'))

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
    release_date = db.Column(db.DateTime)
    spotify_id = db.Column(db.String())

    def __repr__(self):
        return f"Album('{self.title}', '{self.cover_art}')"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(), nullable=False, index=True, unique=True)

    def __repr__(self):
        return f"Genre('{self.tag_name}')"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(200), unique=True, index=True, nullable=False)
    spotify_token = db.Column(db.String(200), unique=False, nullable=True)
