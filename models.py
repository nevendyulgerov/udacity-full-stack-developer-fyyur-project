from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(), default='')
    shows = db.relationship('Show', backref='venue', lazy='dynamic')

    def __init__(self, name, city, state, address, phone, image_link, genres, facebook_link, website, seeking_talent=False, seeking_description=''):
        self.name = name
        self.city = city
        self.state = state
        self.address = address
        self.phone = phone
        self.image_link = image_link
        self.genres = genres
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_talent = seeking_talent
        self.seeking_description = seeking_description

    def __repr__(self):
        return f'<Venue Name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(), default='')
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __init__(self, name, city, state, phone, image_link, genres, facebook_link, website, seeking_venue=False, seeking_description=''):
        self.name = name
        self.city = city
        self.state = state
        self.phone = phone
        self.image_link = image_link
        self.genres = genres
        self.facebook_link = facebook_link
        self.website = website
        self.seeking_venue = seeking_venue
        self.seeking_description = seeking_description

    def __repr__(self):
        return f'<Artist Name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.String(), nullable=False)
