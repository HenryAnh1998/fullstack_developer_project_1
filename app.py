# Imports
import json
import logging
import os
import sys
from logging import FileHandler, Formatter

from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, url_for, abort)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import datetime
from forms import *
from models import *

# App Config.

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)



# Filters.
# Controllers.
from models import *

@app.route('/')
def index():
    return render_template('pages/home.html')

pass

# Artists
# Create Artist


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=json.loads(request.form['seeking_venue'].lower()),
            website=request.form['website'],
            seeking_description=request.form['seeking_description']
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be added')
        db.session.rollback()
    finally:
        db.session.close()

        return render_template('pages/home.html')


# Get Artist


@app.route('/artists')
def artists():
    response = Artist.query.all()
    return render_template('pages/artists.html',
                           artists=response)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given venue_id
    artist = Artist.query.filter(Artist.id == artist_id).first()

    past = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming = db.session.query(Show).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).join(Venue, Show.venue_id == Venue.id).add_columns(Venue.id, Venue.name,
                                                                                             Venue.image_link,
                                                                                             Show.start_time).all()

    upcoming_shows = []

    past_shows = []

    for i in upcoming:
        upcoming_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
            'venue_id': i[1],
            'venue_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    if artist is None:
        abort(404)

    response = {
        "id": artist.id,
        "name": artist.name,
        "genres": [artist.genres],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template('pages/show_artist.html', artist=response)


# Update Artist


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter(Artist.id == artist_id).first()

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.filter(Artist.id == artist_id).first()

        artist.name = request.form['name'],
        artist.city = request.form['city'],
        artist.state = request.form['state'],
        artist.phone = request.form['phone'],
        artist.genres = request.form.getlist('genres'),
        artist.image_link = request.form['image_link'],
        artist.facebook_link = request.form['facebook_link'],
        artist.seeking_venue = json.loads(request.form['seeking_venue'].lower()),
        artist.website = request.form['website'],
        artist.seeking_description = request.form['seeking_description']

        db.session.add(artist)
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    except Exception as e:
        print(e)
        db.session.rollback()
        return redirect(url_for('server_error'))
    finally:
        db.session.close()


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {'count': len(result), 'data': result}

    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=search_term)


# Venues
#  Create Venue


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            genres=request.form.getlist('genres'),
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            website=request.form['website'],
            seeking_talent=json.loads(request.form['seeking_talent'].lower()),
            seeking_description=request.form['seeking_description']
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be added')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues')
def venues():
    areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

    response = []
    for area in areas:

        # Querying venues and filter them based on area (city, venue)
        result = Venue.query.filter(Venue.state == area.state).filter(Venue.city == area.city).all()

        venue_data = []

        # Creating venues' response
        for venue in result:
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
            })

            response.append({
                'city': area.city,
                'state': area.state,
                'venues': venue_data
            })
    return render_template('pages/venues.html', areas=response)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    areas = Venue.query(Venue).filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    data = []
    for venue in areas:
        tmp = {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(venue.shows)}
        data.append(tmp)

    response = {'count': len(data), 'data': data}

    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()

    past = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time < datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
                                                                                                Artist.image_link,
                                                                                                Show.start_time).all()

    upcoming = db.session.query(Show).filter(Show.venue_id == venue_id).filter(
        Show.start_time > datetime.now()).join(Artist, Show.artist_id == Artist.id).add_columns(Artist.id, Artist.name,
                                                                                                Artist.image_link,
                                                                                                Show.start_time).all()

    upcoming_shows = []

    past_shows = []

    for i in upcoming:
        upcoming_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    for i in past:
        past_shows.append({
            'artist_id': i[1],
            'artist_name': i[2],
            'image_link': i[3],
            'start_time': str(i[4])
        })

    if venue is None:
        abort(404)

    response = {
        "id": venue.id,
        "name": venue.name,
        "genres": [venue.genres],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }

    return render_template('pages/show_venue.html', venue=response)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter(Venue.id == venue_id).first()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter(Venue.id == venue_id).first()
    try:
        venue.name = request.form['name'],
        venue.city = request.form['city'],
        venue.state = request.form['state'],
        venue.address = request.form['address'],
        venue.phone = request.form['phone'],
        venue.genres = request.form.getlist('genres'),
        venue.image_link = request.form['image_link'],
        venue.facebook_link = request.form['facebook_link'],
        venue.website = request.form['website'],
        venue.seeking_talent = json.loads(request.form['seeking_talent'].lower()),
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as e:
        print(e)
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be added')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Shows


@app.route('/shows')
def shows():
    data = Show.query.join(Artist, Artist.id == Show.artist_id).join(Venue, Venue.id == Show.venue_id).all()
    print(data)
    response = []
    for show in data:
        response.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html',
                           results=response)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id=request.form['venue_id'],
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Requested show was successfully listed')
    except Exception as e:
        print(e)
        flash('An error occurred. Requested show could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# Launch.

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
