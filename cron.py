#!/usr/bin/env python
from flaskext.mail import Message
from twilio.rest import TwilioRestClient

import urllib
from models import db, Snipe
from soc import Soc
from app import mail, app
import datetime

soc = Soc()

account = "ACd35259f50af04485caaa4c69b779418b"
token = "a918ed53d5c28a74c0abeb911c7f63af"

client = TwilioRestClient(account=account, token=token)

EMAIL_SENDER = "Course Sniper <sniper@vverma.net>"

def poll(subject):
    app.logger.info("Polling for %s" % (subject))
    courses = soc.get_courses(subject)

    open_data = {}
    for course in courses:
        course_number = course['courseNumber']
        open_data[course_number] = []
        for section in course['sections']:
            # section is open
            if section['openStatus']:
                if course_number in open_data:
                    open_data[course_number].append(section['number'])

    # all of these courses are open
    open_courses = [course for course, open_sections in open_data.iteritems() if open_sections]

    snipes = Snipe.query.filter(Snipe.course_number.in_(open_courses))
    for snipe in snipes:
        if snipe.section in open_data[snipe.course_number]:
            notify(snipe)

def notify(snipe):
    course = '%s:%s:%s' % (snipe.subject, snipe.course_number, snipe.section)

    if snipe.user.email:

        attributes = {
            'email': snipe.user.email,
            'phone_number': snipe.user.phone_number,
            'subject': snipe.subject,
            'course_number': snipe.course_number,
            'section': snipe.section,
        }

        url = 'http://sniper.vverma.net/?%s' % (urllib.urlencode(attributes))

        email_text = 'A course (%s) that you were watching looks open. Go register for it! If you don\'t get in, visit this URL: \n\n %s \n\n to continue watching it.\n\n Send any feedback to sniper@vverma.net' % (course, url)

        message = Message('[Course Sniper](%s) is open' %(course), sender=EMAIL_SENDER)
        message.body = email_text
        message.add_recipient(snipe.user.email)

        mail.send(message)

    if snipe.user.phone_number:
        text = 'A course (%s) that you were watching looks open. Go register for it! If you don\'t get in, reply back with "%s" and I\'ll continue watching it' % (course, course)
        message = client.sms.messages.create(to=snipe.user.phone_number, from_="+17326384545", body=text)

    db.session.delete(snipe)
    db.session.commit()

    app.logger.info('Notified user: %s about snipe %s' % (snipe.user, snipe))

        

if __name__ == '__main__':
    # get all the courses that should be queried.
    app.logger.info("----------- Running the Cron %s " % (str(datetime.datetime.now())))
    subjects = db.session.query(Snipe.subject).distinct().all()
    for subject in subjects:
        poll(subject)
