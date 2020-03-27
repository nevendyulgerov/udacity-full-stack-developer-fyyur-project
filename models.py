from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CsrfProtect

db = SQLAlchemy()
csrf = CsrfProtect()


def setup_db(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
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

    def get_base_details(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def get_short_details(self, current_time):
        upcoming_shows = self.shows.filter(Show.start_time > current_time).all()

        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': len(upcoming_shows)
        }

    def get_full_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': self.genres,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description
        }

    def generate_area(self, city, state):
        return {
            'city': city,
            'state': state,
            'venues': [self]
        }

    @staticmethod
    def find_area_index_by_location(areas, city, state):
        target_area_index = -1

        for area_index in range(len(areas)):
            area = areas[area_index]

            if area['city'] == city and area['state'] == state:
                target_area_index = area_index
                break

        return target_area_index

    @staticmethod
    def get_areas_venues(venues_results, current_time):
        areas = []

        for venue in venues_results:
            target_area_index = Venue.find_area_index_by_location(areas, venue.city, venue.state)
            is_new_area = target_area_index == -1
            short_detailed_venue = Venue.get_short_details(venue, current_time)

            if is_new_area:
                venue_area = Venue.generate_area(venue, venue.city, venue.state)
                areas.append(venue_area)
            else:
                areas[target_area_index]['venues'].append(short_detailed_venue)

        return areas


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
    shows = db.relationship('Show', backref='artist', lazy='dynamic')

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

    def get_base_details(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def get_short_details(self, current_time):
        upcoming_shows = self.shows.filter(Show.start_time > current_time).all()

        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': len(upcoming_shows)
        }

    def get_full_details(self):
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'image_link': self.image_link,
            'genres': self.genres,
            'facebook_link': self.facebook_link,
            'website': self.website,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description
        }


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.String(), nullable=False)

    def get_venue_details(self, format_datetime):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.venue.name,
            'venue_image_link': self.venue.image_link,
            'start_time': format_datetime(str(self.start_time))
        }

    def get_artist_details(self, format_datetime):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'artist_image_link': self.artist.image_link,
            'start_time': format_datetime(str(self.start_time))
        }
