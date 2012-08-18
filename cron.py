#!/usr/bin/env python
""" This represents the cronjob that runs to check for course openings"""
from flaskext.mail import Message

import urllib
from models import db, Snipe
from soc import Soc
from app import mail, app, client
import datetime

soc = Soc()

EMAIL_SENDER = "Course Sniper <sniper@vverma.net>"

def poll(subject):
    """ Poll a subject for open courses. """
    app.logger.warning("Polling for %s" % (subject))
    
    # get all the course data from SOC
    courses = soc.get_courses(subject)

    # build information about which courses/sections are currently open.
    open_data = {}
    for course in courses:
        course_number = course['courseNumber']
        open_data[course_number] = []
        for section in course['sections']:
            # section is open
            if section['openStatus']:
                if course_number in open_data:
                    open_data[course_number].append(section['number'])

    # all of these course numbers are open
    open_courses = [course for course, open_sections in open_data.iteritems() if open_sections]

    if open_courses:
        # Notify people that were looking for these courses
        snipes = Snipe.query.filter(Snipe.course_number.in_(open_courses))
        for snipe in snipes:
            if snipe.section in open_data[snipe.course_number]:
                notify(snipe)
    else:
        app.logger.warning('Subject "%s" has no open courses' % (subject))

def notify(snipe):
    """ Notify this snipe that their course is open"""
    course = '%s:%s:%s' % (snipe.subject, snipe.course_number, snipe.section)

    if snipe.user.email:

        attributes = {
            'email': snipe.user.email,
            'phone_number': snipe.user.phone_number,
            'subject': snipe.subject,
            'course_number': snipe.course_number,
            'section': snipe.section,
        }

        # build the url for prepopulated form
        url = 'http://sniper.vverma.net/?%s' % (urllib.urlencode(attributes))

        email_text = 'A course (%s) that you were watching looks open. Go register for it! If you don\'t get in, visit this URL: \n\n %s \n\n to continue watching it.\n\n Send any feedback to sniper@vverma.net' % (course, url)

        # send out the email
        message = Message('[Course Sniper](%s) is open' %(course), sender=EMAIL_SENDER)
        message.body = email_text
        message.add_recipient(snipe.user.email)

        mail.send(message)

    if snipe.user.phone_number:
        # send out a text
        text = 'A course (%s) that you were watching looks open. Go register for it! If you don\'t get in, reply back with "%s" and I\'ll continue watching it' % (course, course)
        message = client.sms.messages.create(to=snipe.user.phone_number, from_="+17326384545", body=text)

    db.session.delete(snipe)
    db.session.commit()

    app.logger.warning('Notified user: %s about snipe %s' % (snipe.user, snipe))

        

if __name__ == '__main__':
    # get all the courses that should be queried.
    app.logger.warning("----------- Running the Cron %s " % (str(datetime.datetime.now())))
    subjects = db.session.query(Snipe.subject).distinct().all()
    for subject in subjects:
        poll(subject)
