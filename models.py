from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/production.db'
db = SQLAlchemy(app)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(8))
    course_number = db.Column(db.String(8))
    snipes = db.relationship("Snipe", backref="course")

    def __init__(self, subject, course_number):
        self.subject = subject
        self.course_number = course_number
    
    def __repr__(self):
        return '%s:%s' % ( self.subject, self.course_number)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(8))
    snipe_id = db.Column(db.Integer, db.ForeignKey('snipe.id'))

    def __init__(self, section):
        self.section = section

    def __repr__(self):
        return self.section

class Snipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(16))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    sections = db.relationship('Section')

    def __init__(self, phone_number, course, sections):
        self.phone_number = phone_number
        self.course = course
        self.sections = sections

    def __repr__(self):
        return '%s %s-%s' % (self.phone_number, self.course, ','.join([str(section) for section in self.sections]))
