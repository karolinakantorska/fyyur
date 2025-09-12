from datetime import datetime
from flask_wtf import Form

from enums import State
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
import re
import enum
from wtforms.validators import AnyOf
from wtforms.validators import ValidationError

def is_valid_phone(number):
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator
    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]
    Note: (? = optional) - Learn more: https://regex101.com/
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)

def validate_phone(form, field):
    if field.data and not is_valid_phone(field.data):
        raise ValidationError("Invalid phone number format.")

def validate_genres(form, field):
    invalid = [g for g in field.data if g not in [genre.value for genre in Genre]]
    if invalid:
        raise ValidationError(f"Invalid genres: {invalid}")
    
class State(enum.Enum):
    AL = 'AL'
    AK = 'AK'
    AZ = 'AZ'
    AR = 'AR'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DE = 'DE'
    DC = 'DC'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    IA = 'IA'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    ME = 'ME'
    MT = 'MT'
    NE = 'NE'
    NV = 'NV'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NY = 'NY'
    NC = 'NC'
    ND = 'ND'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    MD = 'MD'
    MA = 'MA'
    MI = 'MI'
    MN = 'MN'
    MS = 'MS'
    MO = 'MO'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VT = 'VT'
    VA = 'VA'
    WA = 'WA'
    WV = 'WV'
    WI = 'WI'
    WY = 'WY'

    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]
    
class Genre(enum.Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Hip_Hop = 'Hip-Hop'
    Heavy_Metal = 'Heavy Metal'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_n_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

    @classmethod
    def choices(cls):
        """ Methods decorated with @classmethod can be called statically without having an instance of the class."""
        return [(choice.value, choice.value) for choice in cls]
    
class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

    
class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )

    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[validate_phone]
    )

    image_link = StringField(
        'image_link'
    )

    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    web_link = StringField(
        'web_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )
    #def validate(self):
    #    """Custom validate method"""
    #    rv = FlaskForm.validate(self)
    #    if not rv:
    #        return False
    #    if not is_valid_phone(self.phone.data):
    #        self.phone.errors.append('Invalid phone.')
    #        return False
    #    # if pass validation
    #    return True


class ArtistForm(Form):

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        'phone',
        validators=[validate_phone]
    )

    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(),validate_genres],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        # TODO-notdone implement enum restriction
        'facebook_link', validators=[URL()]
     )

    web_link = StringField(
        'web_link'
     )

    is_seeking = BooleanField( 'is_seeking' )

    seeking_description = StringField(
            'seeking_description'
     )
    #def validate(self):
    #    """Custom validate method"""
    #    rv = FlaskForm.validate(self)
    #    if not rv:
    #        return False
    #    if not is_valid_phone(self.phone.data):
    #        self.phone.errors.append('Invalid phone.')
    #        return False
    #    # if pass validation
    #    return True