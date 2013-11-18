""" Represents the persistent models for the sniper application"""
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/production.db'
db = SQLAlchemy(app)

class Snipe(db.Model):
    """ A snipe model represents the course info pertaining to a snipe"""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(8))
    course_number = db.Column(db.String(8))
    section = db.Column(db.String(8))
    # set up the many to one relationship with the User model.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls, email, subject, course_number, section):
        """ Creates a snipe, and its corresponding user if they don't already exist"""
        # see if the user exists already
        user = User.query.filter_by(email=email).first()

        if not user:
            return Snipe(email, subject, course_number, section)

        # see if the snipe exists already
        snipe = Snipe.query.filter_by(user=user, subject=subject, course_number=course_number, section=section).first()
        if not snipe:
            return Snipe(email, subject, course_number, section)

        return snipe



    def __init__(self, email, subject, course_number, section):
        user = User.query.filter_by(email=email).first()
        if user:
            self.user = user
        else:
            user = User(email)
        
        self.subject = subject
        self.course_number = course_number
        self.section = section
        self.user = user

    def __repr__(self):
        return '(%s:%s:%s)' % (self.subject, self.course_number, self.section)

class User(db.Model):
    """ Represents a user in the database (phone_number and email pair). """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(16))
    # Set up the one to many relationship with the Snipe model.
    snipes = db.relationship('Snipe', backref='user')

    def __init__(self, email=None, phone_number=None):
        if not email:
            raise Exception('I don\'t have an email for a user')

        self.email = email

    def __repr__(self):
        return '(%s)' % (self.email)
