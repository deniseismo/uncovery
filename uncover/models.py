from uncover import db

tags = db.Table(
    'tags',
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
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

    def __repr__(self):
        return f"Album('{self.title}', '{self.cover_art}')"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(), nullable=False, unique=True)

    def __repr__(self):
        return f"Genre('{self.tag_name}')"

# <div id="form">
#     <div class="bar">
#         <div class="label">the times they are a-changin'</div>
#         <div id="r-slider"></div>
#     </div>
# </div>
