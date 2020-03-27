# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
import os
import sys
from models import setup_db, Venue, Artist, Show
from utils.forms import get_form_error

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = setup_db(app)

# ----------------------------------------------------------------------------#
# Filters.
# # ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


def get_current_time(format='%Y-%m-%d %H:%S:%M'):
    return datetime.now().strftime(format)


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues_results = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    areas = Venue.get_areas_venues(venues_results, get_current_time())

    return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    error = False
    results_list = []
    search_term = request.form.get('search_term', '')

    try:
        results_query = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
        results_list = list(map(Venue.get_base_details, results_query))
    except:
        error = True
        print(sys.exc_info())

    if error:
        server_error()
    else:
        results = {
            'count': len(results_list),
            'data': results_list
        }
        return render_template('pages/search_venues.html', results=results, search_term=search_term)


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    current_time = get_current_time()
    error = False
    body = {}

    try:
        venue = Venue.query.get(venue_id)
        upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
        past_shows = venue.shows.filter(Show.start_time < current_time).all()
        upcoming_shows_data = []
        past_shows_data = []

        for show in upcoming_shows:
            artist_details = Show.get_artist_details(show, format_datetime)
            upcoming_shows_data.append(artist_details)

        for show in past_shows:
            artist_details = Show.get_artist_details(show, format_datetime)
            past_shows_data.append(artist_details)

        body = Venue.get_full_details(venue)
        body['past_shows'] = past_shows_data
        body['upcoming_shows'] = upcoming_shows_data
        body['past_shows_count'] = len(past_shows)
        body['upcoming_shows_count'] = len(upcoming_shows)
    except:
        error = True
        print(sys.exc_info())

    if error:
        not_found_error()
    else:
        return render_template('pages/show_venue.html', venue=body)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    form = {}
    default_error_message = 'An error occurred. Venue ' + request.form['name'] + ' could not be listed.'
    error_message = default_error_message

    try:
        form = VenueForm(request.form)

        if not form.validate():
            error_message = get_form_error(form, default_error_message)
            raise ValidationError

        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            website=form.website.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )

        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(error_message, 'error')
        return render_template('forms/new_venue.html', form=form)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!', 'success')
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    body = {}

    try:
        venue = Venue.query.get(venue_id)
        body = Venue.get_base_details(venue)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        server_error()
    else:
        return jsonify(body)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    error = False
    artists = []

    try:
        artists = Artist.query.all()
    except:
        error = False
        print(sys.exc_info())

    if error:
        server_error()
    else:
        return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    error = False
    results = {}
    search_term = request.form.get('search_term', '')

    try:
        artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
        results = {
            'count': len(artists),
            'data': artists
        }
    except:
        error = True
        print(sys.exc_info())

    if error:
        server_error()
    else:
        return render_template('pages/search_artists.html', results=results, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    current_time = get_current_time()
    error = False
    body = {}

    try:
        artist = Artist.query.get(artist_id)
        upcoming_shows = artist.shows.filter(Show.start_time > current_time).all()
        past_shows = artist.shows.filter(Show.start_time < current_time).all()
        upcoming_shows_data = []
        past_shows_data = []

        for show in upcoming_shows:
            venue_details = Show.get_venue_details(show, format_datetime)
            upcoming_shows_data.append(venue_details)

        for show in past_shows:
            venue_details = Show.get_venue_details(show, format_datetime)
            past_shows_data.append(venue_details)

        body = Artist.get_full_details(artist)
        body['past_shows'] = past_shows_data
        body['upcoming_shows'] = upcoming_shows_data
        body['past_shows_count'] = len(past_shows)
        body['upcoming_shows_count'] = len(upcoming_shows)

    except:
        error = True
        print(sys.exc_info())

    if error:
        not_found_error()
    else:
        return render_template('pages/show_artist.html', artist=body)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    error = False
    artist = {}

    try:
        artist = Artist.query.get(artist_id)
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.image_link.data = artist.image_link
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.website.data = artist.website
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
    except:
        error = True
        print(sys.exc_info())

    if error:
        not_found_error()
    else:
        return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    default_error_message = 'An error occurred. Artist ' + request.form['name'] + ' could not be updated.'
    error_message = default_error_message

    try:
        form = ArtistForm(request.form)

        if not form.validate():
            error_message = get_form_error(form, default_error_message)
            raise ValidationError

        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(error_message, 'error')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully updated!', 'success')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    error = False
    venue = None

    try:
        venue = Venue.query.get(venue_id)
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.image_link.data = venue.image_link
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.website.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
    except:
        error = True
        print(sys.exc_info())

    if error:
        not_found_error()
    else:
        return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    default_error_message = 'An error occurred. Venue ' + request.form['name'] + ' could not be updated.'
    error_message = default_error_message

    try:
        form = VenueForm(request.form)

        if not form.validate():
            error_message = get_form_error(form, default_error_message)
            raise ValidationError

        venue = Venue.query.get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.image_link = request.form['image_link']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.seeking_talent = request.form.get('seeking_talent', default=False, type=bool)
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(error_message, 'error')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully updated!', 'success')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False

    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            genres=request.form.getlist('genres'),
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            seeking_venue=request.form.get('seeking_venue', default=False, type=bool),
            seeking_description=request.form['seeking_description']
        )
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.', 'error')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!', 'success')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    error = False
    data = []

    try:
        shows = Show.query.order_by(db.desc(Show.start_time))

        for show in shows:
            data.append({
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': format_datetime(str(show.start_time))
            })
    except:
        error = True
        print(sys.exc_info())

    if error:
        not_found_error()
    else:
        return render_template('pages/shows.html', shows=data)
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    default_error_message = 'An error occurred. The show could not be saved.'
    error_message = default_error_message

    try:
        form = ShowForm(request.form)

        if not form.validate():
            error_message = get_form_error(form, default_error_message)
            raise ValidationError

        show = Show(
            venue_id=form.venue_id.data,
            artist_id=form.artist_id.data,
            start_time=form.start_time.data
        )

        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        flash(error_message, 'error')
    else:
        flash('Show was successfully listed!', 'success')

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
'''
if __name__ == '__main__':
    app.run()
'''

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
