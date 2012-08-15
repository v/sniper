""" This file sets up the Flask Application for sniper.
    Sniper is an application that hits the Rutgers SOC API and notifies users when a class opens up. """

from flask import Flask, render_template, request
from wtforms import Form, TextField, validators
from wtforms.validators import StopValidation
from models import Snipe, db, User
from twilio.rest import TwilioRestClient
from flaskext.mail import Mail
from secrets import mail_username, mail_password, twilio_account, twilio_token
import re

import logging
from logging import Formatter, FileHandler

# Set up the Flask application
app = Flask(__name__)

# Set up a file for logging
file_handler = FileHandler('everything.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)

# Set up gmail SMTP connection for sending mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] =  587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password

mail = Mail(app)

# Set up a twilio client for sending texts out
client = TwilioRestClient(account=twilio_account, token=twilio_token)


class SnipeForm(Form):
    """ Represents the Snipe form on the homepage. """
    email = TextField('Email', [validators.Email()])
    phone_number = TextField('Phone Number', [validators.Length(min=9, max=12), validators.NumberRange()])
    subject = TextField('Subject', [validators.Length(min=2, max=4), validators.NumberRange()])
    course_number = TextField('Course Number', [validators.Length(min=2, max=4), validators.NumberRange()])
    section = TextField('Section', [validators.Length(min=1, max=4)])

    def validate_email(form, field):
        """ Checks that either the phone number or the email is set"""
        if form.email.data and form.phone_number.data:
            return True
        elif form.phone_number.data:
            form.email.errors[:] = []
            return True
        elif form.email.data:
            form.phone_number.errors[:] = []
            return True
        raise StopValidation('You must either enter a phone number or an email address.')

    def save(self):
        """ Saves to SQLAlchemy User and Snipe models """
        
        # Remove '+1's from phone numbers
        self.phone_number.data = self.phone_number.data.lstrip('+1')
        snipe = Snipe.create(self.phone_number.data, self.email.data, self.subject.data, self.course_number.data, self.section.data)

        db.session.add(snipe)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Handles the home page rendering."""
    form = SnipeForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save()
        return render_template('success.html', form=form)
    if not request.form:
        # this trick allows us to prepopulate entries using links sent out in emails.
        form = SnipeForm(request.args)
    return render_template('home.html', form=form)

@app.route('/twilio_callback', methods=['GET', 'POST'])
def twilio_callback():
    """ Handles the callback from twilio """
    course_info = request.form['Body']
    
    # Regex to search for subject:course_num:section in the text message.
    m = re.search('([\w\d]+):([\w\d]+):([\w\d]+)', course_info)
    if m:
        subject = m.group(1)
        course_number = m.group(2)
        section = m.group(3)

        # Twilio always puts +1s at the beginning of phone numbers
        phone_number = request.form['From'].lstrip('+1')

        # check if the user already exists
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            email = user.email
        else:
            email = None


        snipe = Snipe.create(phone_number, email, subject, course_number, section)

        db.session.add(snipe)
        db.session.commit()

        # Notify the user via text message.
        text = "I'm on it. Watching %s:%s:%s for you." % (subject, course_number, section)
        client.sms.messages.create(to=snipe.user.phone_number, from_="+17326384545", body=text)

        return 'Lovely job Twilio!'
    else:
        # log errors.
        app.logger.error('There is sadness with text messages')
        app.logger.error('Message: %s Other %s' % (request.form['Body'], str(request.form)))

        return 'Saddness in the world'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
