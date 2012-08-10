from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/production.db'
db = SQLAlchemy(app)

class Snipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(16))
    subject = db.Column(db.String(8))
    course_number = db.Column(db.String(8))
    section = db.Column(db.String(8))

    def __init__(self, phone_number, email, subject, course_number, section):
        self.phone_number = phone_number
        self.email = email
        self.subject = subject
        self.course_number = course_number
        self.section = section

    def __repr__(self):
        return '(%s)-(%s:%s:%s)' % (self.phone_number, self.subject, self.course_number, self.section)
