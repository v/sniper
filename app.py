""" This file sets up the Flask Application for sniper.
    Sniper is an application that hits the Rutgers SOC API and notifies users when a class opens up. """

from flask import Flask, render_template, request
from wtforms import Form, TextField, validators
from wtforms.validators import StopValidation
from models import Snipe, db, User
from flaskext.mail import Mail
from secrets import mail_username, mail_password
from soc import Soc
from werkzeug.contrib.fixers import ProxyFix
import re
import json

import logging
from logging import Formatter, FileHandler

# Set up the Flask application
app = Flask(__name__)

# Set up a file for logging
file_handler = FileHandler('everything.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)

app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

class SnipeForm(Form):
    """ Represents the Snipe form on the homepage. """
    email = TextField('Email', [validators.Email(), validators.Required()])
    subject = TextField('Subject')
    course_number = TextField('Course Number', [validators.Length(min=2, max=4), validators.NumberRange()])
    section = TextField('Section', [validators.Length(min=1, max=4)])

    def validate_subject(form, field):
        if not form.subject.data.isdigit():
            m = re.search('(\d+)', form.subject.data)
            if m:
                form.subject.data = m.group(1)
            else:
                raise StopValidation('Please enter a valid subject')
        return True

    def validate_course_number(form, field):
        # course numbers sometime have leading zeroes
        if form.course_number.data.isdigit():
            form.course_number.data = str(int(form.course_number.data))
        return True

    def validate_section(form, field):
        if form.section.data.isdigit():
            form.section.data = str(int(form.section.data))
        return True

    def save(self):
        """ Saves to SQLAlchemy User and Snipe models """

        snipe = Snipe.create(self.email.data, self.subject.data, self.course_number.data, self.section.data)

        db.session.add(snipe)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Handles the home page rendering."""

    soc = Soc()
    subjects = soc.get_subjects()

    form = SnipeForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save()
        return render_template('success.html', form=form)
    if not request.form:
        # this trick allows us to prepopulate entries using links sent out in emails.
        form = SnipeForm(request.args)

    return render_template('home.html', form=form, subjects=subjects)

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

@app.route('/test', methods=['GET', 'POST'])
def ajaxtest():
    result = {
        'success': test(),
    }

    if not result['success']:
        from cron import EMAIL_SENDER
        from flaskext.mail import Message

        message = Message('Sniper tests are failing', sender=EMAIL_SENDER)
        message.body = 'FIX IT'
        message.add_recipient('vaibhav2614@gmail.com')
        mail.send(message)

    return json.dumps(result)

def test():
    from cron import poll

    soc = Soc()
    math_courses = soc.get_courses(640)
    open_courses = poll(640, result = True)
    for dept, sections in open_courses.iteritems():
        open_courses[dept] = [section.number for section in sections]

    success = True

    for math_course in math_courses:
        course_number = math_course['courseNumber']

        if course_number.isdigit():
            course_number = str(int(course_number))

        for section in math_course['sections']:
            section_number = section['number']
            if section_number.isdigit():
                section_number = str(int(section_number))

            if section['openStatus'] and not section_number in open_courses[course_number]:
                raise Exception('Test failed')
                success = False

    return success

if __name__ == '__main__':
    test()
    app.run(host='0.0.0.0', debug=True)
