#from flask.ext.wtf import Form, TextField, RadioField
from flask_wtf import Form

from wtforms import TextField

# search form
class SearchForm (Form):
    search_text = TextField ('search_text')
    # search_type = RadioField ('search_type', choices=[('term','free-text'), ('cond','condition'), ('intr', 'intervention'), ('outc', 'outcome')], default='term')
  
