#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import datetime, ShowForm, ArtistForm, VenueForm
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO: Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String)) 
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_link = db.Column(db.String(500))
    shows = db.relationship(
      'Show', 
      backref='venue', 
      lazy=True,
      cascade="all, delete-orphan",
      passive_deletes=True
      )
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_seeking = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1000))
    
    
    # TODO-done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String)) 
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    web_link = db.Column(db.String(500))
    shows = db.relationship(
      'Show', 
      backref='artist', 
      lazy=True,
      cascade="all, delete-orphan",
      passive_deletes=True
      )
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_seeking = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(1000))
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    
class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ondelete="CASCADE"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id', ondelete="CASCADE"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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

class Area:
    def __init__(self, city, state, venues):
      self.city = city
      self.state = state
      self.venues = venues
      
class venue_data:
  def __init__(self, id, name, num_upcoming_shows):
    self.id = id
    self.name = name
    self.num_upcoming_shows = num_upcoming_shows
    
class shows_data:
  def __init__(self, venue_id,venue_name, venue_image_link,start_time):
    self.venue_id= venue_id
    self.venue_name = venue_name
    self.venue_image_link = venue_image_link
    self.start_time = start_time

@app.route('/venues')
def venues():
  # TODO: implement shows and count of shows
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  
    
  data=Venue.query.all()
  areas = []

  for venue in data:

    if any(area.city == venue.city and area.state == venue.state for area in areas):
      area = next(area for area in areas if area.city == venue.city and area.state == venue.state)
      area.venues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len([show for show in venue.shows if show.date > datetime.now()])
    })
        
    else:
      new_area_venue =venue_data(
        id=venue.id,
        name=venue.name,
        num_upcoming_shows=len([show for show in venue.shows if show.date > datetime.now()])
      )
      area = Area(
        venue.city, 
        venue.state, 
        [new_area_venue]
      )
      areas.append(area)
  
  
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data= Venue.query.filter(Venue.name.ilike(f"%{request.form.get('search_term', '')}%")).all()
  data_venue=[]
  for d in data:
    rsp= search_data(d.id, d.name, len([show for show in d.shows if show.date > datetime.now()]) )#num_upcoming_shows = len([show for show in d.shows if show.date > datetime.now()])
    data_venue.append(rsp)
    
  response = search_response(
    count=len(data),
    data=data_venue
  )

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

class venues_data:
  def __init__(self, id, name, gernes,adress, city, state, phone, web_link, facebook_link, is_seeking, seeking_description, image_link, past_shows, upcoming_shows, past_shows_count, upcoming_shows_count):
    self.id = id
    self.name = name
    self.gernes = gernes
    self.adress = adress
    self.city = city
    self.state = state
    self.phone = phone
    self.web_link = web_link
    self.facebook_link = facebook_link
    self.is_seeking = is_seeking
    self.seeking_description = seeking_description
    self.image_link = image_link
    self.past_shows = past_shows
    self.upcoming_shows = upcoming_shows
    self.past_shows_count = past_shows_count
    self.upcoming_shows_count = upcoming_shows_count
    
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data =Venue.query.get_or_404(venue_id)

  shows =Show.query.join(Artist).filter(Show.venue_id==venue_id)


  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0

      
  for show in data.shows:

    current_show = shows_data(
      show.artist.id,
      show.artist.name,
      show.artist.image_link,
      show.date.strftime('%Y-%m-%d %H:%M:%S'),

    )

    if show.date < datetime.now():
      past_shows.append(current_show)
      past_shows_count += 1
    else:
      upcoming_shows.append(current_show)
      upcoming_shows_count += 1
            
  venue_data = venues_data(
      id=data.id,
      name=data.name,
      gernes=data.genres,
      adress=data.address,
      city=data.city,
      state=data.state,
      phone=data.phone,
      web_link=data.web_link,
      facebook_link=data.facebook_link,
      is_seeking=data.is_seeking,
      seeking_description=data.seeking_description,
      image_link=data.image_link,
      past_shows=past_shows,
      upcoming_shows=upcoming_shows,
      past_shows_count=past_shows_count,
      upcoming_shows_count=upcoming_shows_count
    )

  print(f"Venue Data: {venue_data.web_link}")
  return render_template('pages/show_venue.html', venue=venue_data, shows=shows, now=datetime.now() )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue=Venue(
        genres=request.form.getlist('genres'),
        is_seeking =request.form.get('is_seeking') == 'y',
      )
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except ValueError as e:
      print(e)
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  try:
    venue = Venue.query.get_or_404(venue_id)

    db.session.delete(venue)
    db.session.commit()
    return jsonify({"success": True, "message": "Venue deleted"}), 200
  except ValueError as e:
    db.session.rollback()
    print(e)
    return jsonify({"success": False, "message": "An error occurred"}), 500
  finally:
    db.session.close()


#  Artists
#  ----------------------------------------------------------------
class artists_data:
  def __init__(self, id, name, gernes, city, state, phone, web_link, facebook_link, is_seeking, seeking_description, image_link, past_shows, upcoming_shows, past_shows_count, upcoming_shows_count):
    self.id = id
    self.name = name
    self.gernes = gernes
    self.city = city
    self.state = state
    self.phone = phone
    self.web_link = web_link
    self.facebook_link = facebook_link
    self.is_seeking = is_seeking
    self.seeking_description = seeking_description
    self.image_link = image_link
    self.past_shows = past_shows
    self.upcoming_shows = upcoming_shows
    self.past_shows_count = past_shows_count
    self.upcoming_shows_count = upcoming_shows_count
    


@app.route('/artists')

  
def artists():
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

class search_response:
  def __init__(self, count, data):
    self.count= count
    self.data = data
    
class search_data :
  def __init__(self, id, name, num_upcoming_shows):
    self.id= id
    self.name = name
    self.num_upcoming_shows = num_upcoming_shows
      
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO-done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return " The Wild Sax Band".

  data= Artist.query.filter(Artist.name.ilike(f"%{request.form.get('search_term', '')}%")).all()
  data_artist=[]
  for d in data:
    rsp= search_data(d.id, d.name, len([show for show in d.shows if show.date > datetime.now()]) )#num_upcoming_shows = len([show for show in d.shows if show.date > datetime.now()])
    data_artist.append(rsp)
  
  response = search_response(
    count=len(data),
    data=data_artist
  )
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist =Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
    
  for show in artist.shows:
      current_show = shows_data(
          show.venue.id,
          show.venue.name,
          show.venue.image_link,
          show.date.strftime('%Y-%m-%d %H:%M:%S')
      )
      if show.date < datetime.now():
        past_shows.append(current_show)
        past_shows_count += 1
      else:
        upcoming_shows.append(current_show)
        upcoming_shows_count += 1

  artist_data = artists_data(
      id=artist.id,
      name=artist.name,
      gernes=artist.genres,
      city=artist.city,
      state=artist.state,
      phone=artist.phone,
      web_link=artist.web_link,
      facebook_link=artist.facebook_link,
      is_seeking=artist.is_seeking,
      seeking_description=artist.seeking_description,
      image_link=artist.image_link,
      past_shows=past_shows,
      upcoming_shows=upcoming_shows,
      past_shows_count=past_shows_count,
      upcoming_shows_count=upcoming_shows_count
    )   
  print(f"Artist Data: {artist_data.web_link}")
  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  data =Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=data)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  data =Artist.query.get_or_404(artist_id)
  form = ArtistForm(request.form)
  try:
    form.populate_obj(data)
    new_artist=Artist(
      is_seeking =request.form.get('is_seeking') == 'y',
      genres=request.form.getlist('genres'),
      id = artist_id
    )
    
    data= new_artist
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  data =Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=data)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  data =Venue.query.get_or_404(venue_id)
  form = VenueForm(request.form)
  try:
    form.populate_obj(data)
    new_venue=Venue(
      is_seeking =request.form.get('is_seeking') == 'y',
      genres=request.form.getlist('genres'),
      id = venue_id
    )
    
    data= new_venue
    db.session.commit()
    flash('Venuet ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  form = ArtistForm(request.form)
  try:
    artist=Artist(
       genres=request.form.getlist('genres'),
       is_seeking =request.form.get('is_seeking') == 'y',
       )
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

  try:
    artist = Artist.query.get_or_404(artist_id)

    db.session.delete(artist)
    db.session.commit()
    return jsonify({"success": True, "message": "Artist deleted"}), 200
  except ValueError as e:
    db.session.rollback()
    print(e)
    return jsonify({"success": False, "message": "An error occurred"}), 500
  finally:
    db.session.close()
    


#  Shows
#  ----------------------------------------------------------------
class ShowData:
    def __init__(self, venue_id, venue_name, artist_id, artist_name, artist_image_link, start_time):
      self.venue_id = venue_id
      self.venue_name = venue_name
      self.artist_id = artist_id
      self.artist_name = artist_name
      self.artist_image_link = artist_image_link
      self.start_time = start_time
      
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO- DONE: replace with real venues data.
  

  shows=Show.query.all()
  
  data = []
  for show in shows:
    show_data = ShowData(
      venue_id=show.venue_id,
      venue_name=show.venue.name,
      artist_id=show.artist_id,
      artist_name=show.artist.name,
      artist_image_link=show.artist.image_link,
      start_time=show.date.strftime('%Y-%m-%d %H:%M:%S')
    )
    data.append(show_data)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/search', methods=['POST'])
def search_shows():
  data = Show.query.join(Artist).join(Venue).filter(
    Artist.name.ilike(f"%{request.form.get('search_term', '')}%") | 
    Venue.name.ilike(f"%{request.form.get('search_term', '')}%")
  ).all()
  #data= Show.query.filter(Show.artist_id.ilike(f"%{request.form.get('search_term', '')}%") | Show.venue.name.ilike(f"%{request.form.get('search_term', '')}%")).all()

  data_show=[]
  for show in data:
    rsp= ShowData(
      venue_id=show.venue_id,
      venue_name=show.venue.name,
      artist_id=show.artist_id,
      artist_name=show.artist.name,
      artist_image_link=show.artist.image_link,
      start_time=show.date.strftime('%Y-%m-%d %H:%M:%S')
    )
    data_show.append(rsp)
    
  response = search_response(
    count=len(data),
    data=data_show
  )

  return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  form = ShowForm(request.form)
  try:
    show=Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      date=request.form['start_time']
    )
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    
  except ValueError as e:
    print(e)
    flash('An error occurred. Show could not be listed.')
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
