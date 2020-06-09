#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#from lesson 6 3.Flask-Migrate - Part 1
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
#from lesson 6 3.Flask-Migrate - Part 1
migrate = Migrate(app, db)

# done: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #add missinng fields from Data existance
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))
    """ get help from lesson7 11.One-to-Many Relationship Setup and
    from  https://www.youtube.com/watch?time_continue=2&v=juPQ04_twtA&feature=emb_logo """
    show = db.relationship('Show', backref='venue', lazy=True)


    # DONE: implement any missing fields, as a database migration using Flask-Migrate

   

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #add missinng fields from Data existance
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))
    """ get help from lesson7 11.One-to-Many Relationship Setup and
    from  https://www.youtube.com/watch?time_continue=2&v=juPQ04_twtA&feature=emb_logo """
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    # done: implement any missing fields, as a database migration using Flask-Migrate

# done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#get help from https://knowledge.udacity.com/questions/108656 and lesson7 11.One-to-Many Relationship Setup

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
  
    def __repr__(self):
      return f'<Show {self.id} {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  # The error 'NoneType' object has no attribute 'days' corrected by'https://knowledge.udacity.com/questions/70223
  return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  upcoming_shows = []
  venues = Venue.query.all()
  shows = Show.query.all()
  city_and_state = {(venue.city, venue.state) for venue in venues}
  data = [{'city': location[0], 'state': location[1], 'venues': []} for location in city_and_state]
  for item in data:
     upcoming_shows=[]
     for venue in Venue.query.filter_by(city=item['city']).all():
       upcoming_shows = [show for show in venue.show if show.start_time > datetime.now()]
       item['venues'].append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': len(upcoming_shows)})


  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()       
  data=[]
  for venue in results:
    upcoming_shows = [show for show in venue.show if show.start_time > datetime.now()]
    data.append({"id":venue.id,"name":venue.name,"num_upcoming_shows":len(upcoming_shows)})
  response={
    "count": len(results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  #get help from https://knowledge.udacity.com/questions/94121

  venue = Venue.query.get(venue_id)
  data={}
  if venue:
    past_shows=[]
    next_shows=[]
    showP =db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
    showN =db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
    past_shows_count=len(showP)
    next_shows_count=len(showN)
    for show in showP:
      past_shows.append({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": str(show.start_time)
        })
    for show in showN:
      next_shows.append({
          "artist_id": show.artist_id,
          "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
          "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
          "start_time": str(show.start_time)
        })

    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows":  past_shows,
      "upcoming_shows": next_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": next_shows_count
    }
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  # DONE: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  # DONE: modify data to be the data object returned from db insertion
  try:
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                    phone=form.phone.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website="", image_link="",
                    seeking_talent=True,
                    seeking_description="")
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('error. Venue ' + request.form['name'] + ' failed to be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')




@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue) 
      flash('Venue ' + request.form['name'] + ' was successfully deleted!')
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error: 
      print(venue_id)
      print('An error occurred. Venue could not be deleted.')
  if not error: 
      print('Venue  was successfully deleted.')
    
    
  return jsonify({ 'success': True })

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data=[]
  artists = Artist.query.all()
  data = [{'id':artist.id , 'name': artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()       
  data=[]
  for artist in results:
    upcoming_shows = [show for show in artist.show if show.start_time > datetime.now()]
    data.append({"id":artist.id,"name":artist.name,"num_upcoming_shows":len(upcoming_shows)})
  response={
    "count": len(results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  data={}
  if artist:
    past_shows=[]
    next_shows=[]
    showP =db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<=datetime.now()).all()
    showN =db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
    past_shows_count=len(showP)
    next_shows_count=len(showN)
    for show in showP:
      past_shows.append({
        'venue_id' : show.venue_id,
        'venue_name' : Venue.query.filter_by(id=show.venue_id).first().name,
        'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
        'start_time': str(show.start_time)
      })
    for show in showN:
      next_shows.append({
        'venue_id' : show.venue_id,
        'venue_name' : Venue.query.filter_by(id=show.venue_id).first().name,
        'venue_image_link': Venue.query.filter_by(id=show.venue_id).first().image_link,
        'start_time': str(show.start_time)
        })


    data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows":  past_shows,
      "upcoming_shows": next_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": next_shows_count
    }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm(request.form)
  artist_query = Artist.query.get(artist_id)

  artist={
    "id": artist_id,
    "name": artist_query.name,
    "genres": artist_query.genres,
    "city": artist_query.city,
    "state": artist_query.state,
    "phone": artist_query.phone,
    "website": "",
    "facebook_link": artist_query.facebook_link,
    "seeking_venue": True,
    "seeking_description": "",
    "image_link": ""
  }
  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = VenueForm(request.form)
  artist = Artist.query.get(artist_id)
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.facebook_link =form.facebook_link.data
    artist.website = ""
    artist.image_link = ""
    artist.seeking_venue = True
    artist.seeking_description = ""
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('error. artist ' + request.form['name'] + ' failed to be updated.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = Venue.query.get(venue_id)

  venue={
    "id": venue_id,
    "name": venue_query.name,
    "genres": venue_query.genres,
    "address": venue_query.address,
    "city": venue_query.city,
    "state": venue_query.state,
    "phone": venue_query.phone,
    "website": "",
    "facebook_link": venue_query.facebook_link,
    "seeking_talent": True,
    "seeking_description": "",
    "image_link": ""
  }
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link =form.facebook_link.data
    venue.website = ""
    venue.image_link = ""
    venue.seeking_talent = True
    venue.seeking_description = ""
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('error. Venue ' + request.form['name'] + ' failed to be updated.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  form = ArtistForm(request.form)
  try:
    # DONE: modify data to be the data object returned from db insertion
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data,
                    genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website="", image_link="",
                    seeking_venue=False,
                    seeking_description="")
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows = Show.query.all()
  data = [{'venue_id':show.venue_id,
           'venue_name':show.venue.name,
           'artist_id':show.artist.id,
           'artist_name':show.artist.name,
           'artist_image_link':show.artist.image_link,
           'start_time':str(show.start_time)

   } for show in shows]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)
  try:
    show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data,
                start_time=form.start_time.data)
    flash('Show was successfully listed')
    db.session.add(show)
    db.session.commit()

  except:
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
