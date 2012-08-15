from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/production.db'
db = SQLAlchemy(app)

class Snipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(8))
    course_number = db.Column(db.String(8))
    section = db.Column(db.String(8))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def create(cls, phone_number, email, subject, course_number, section):
        user = User.query.filter_by(phone_number=phone_number, email=email).first()

        if not user:
            return Snipe(phone_number, email, subject, course_number, section)

        snipe = Snipe.query.filter_by(user=user, subject=subject, course_number=course_number, section=section).first()
        if not snipe:
            return Snipe(phone_number, email, subject, course_number, section)

        return snipe



    def __init__(self, phone_number, email, subject, course_number, section):
        user = User.query.filter_by(phone_number=phone_number, email=email).first()
        if user:
            self.user = user
        else:
            user = User(email, phone_number)
        
        self.subject = subject
        self.course_number = course_number
        self.section = section
        self.user = user

    def __repr__(self):
        return '(%s:%s:%s)' % (self.subject, self.course_number, self.section)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    phone_number = db.Column(db.String(16))
    snipes = db.relationship('Snipe', backref='user')

    def __init__(self, email=None, phone_number=None):
        if not email and not phone_number:
            raise ValidationError('I don\'t have a phone number or an email for a user')

        self.email = email
        self.phone_number = phone_number.lstrip('+1')

    def __repr__(self):
        return '(%s - %s)' % (self.email, self.phone_number)
