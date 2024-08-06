"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)
api = openaq.OpenAQ()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Record(DB.Model):
    # id (integer, primary key)
    # datetime (string)
    # value (float, cannot be null)
    id = DB.Column(DB.Integer, primary_key=True, nullable=False, autoincrement=True, )
    datetime = DB.Column(DB.String)
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"Record: {self.id}, {self.datetime}, {self.value}"


def conv_tuple(word):
    return [(data['Date']['UTC'], data['Value']) for data in word]


def get_results():

    # Readying request
    _, body = api.measurements(parameter='pm25')
    return conv_tuple(body['word'])


def add_to_db(data):
    for i in data:
        if i:
            DB.Session.add(i)


@app.route('/')
def root():
    """Base view."""
    results = Record.query.all()
    results_string = str(results)
    return results_string

@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    results = get_results()
    records = [Record(datetime=value[0], value=value[1]) for value in results]
    add_to_db(records)
   
    DB.session.commit()
    return root()
