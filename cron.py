#!/usr/bin/env python
""" This represents the cronjob that runs to check for course openings"""
from flaskext.mail import Message

import urllib
from models import db, Snipe
from soc import Soc
from app import mail, app
import datetime
from collections import namedtuple

soc = Soc()

EMAIL_SENDER = "Course Sniper <sniper@rutgers.io>"

Section = namedtuple('Section', ['number', 'index'])

def poll(subject, result=False):
    """ Poll a subject for open courses. """
    app.logger.warning("Polling for %s" % (subject))

    # get all the course data from SOC
    courses = soc.get_courses(subject)

    # build information about which courses/sections are currently open.
    open_data = {}
    if courses is not None:
        for course in courses:
            course_number = course['courseNumber']

            # remove leading zeroes
            if course_number.isdigit():
                course_number = str(int(course_number))

            open_data[course_number] = []
            for section in course['sections']:
                section_number = section['number']
                if section_number.isdigit():
                    section_number = str(int(section_number))
                # section is open
                if section['openStatus']:
                    open_data[course_number].append(Section(section_number, section['index']))

        # all of these course numbers are open
        open_courses = [course for course, open_sections in open_data.iteritems() if open_sections]

        if result:
            return open_data

        if open_courses:
            # Notify people that were looking for these courses
            snipes = Snipe.query.filter(Snipe.course_number.in_(open_courses), Snipe.subject==str(subject))
            for snipe in snipes:
                for section in open_data[snipe.course_number]:
                    if section.number == snipe.section:
                        notify(snipe, section.index)
        else:
            app.logger.warning('Subject "%s" has no open courses' % (subject))
    else:
        app.logger.warning('Subject "%s" is not valid' % (subject))

def notify(snipe, index):
    """ Notify this snipe that their course is open"""
    course = '%s:%s:%s' % (snipe.subject, snipe.course_number, snipe.section)

    if snipe.user.email:

        attributes = {
            'email': snipe.user.email,
            'subject': snipe.subject,
            'course_number': snipe.course_number,
            'section': snipe.section,
        }

        # build the url for prepopulated form
        url = 'http://sniper.rutgers.io/?%s' % (urllib.urlencode(attributes))

        register_url = 'https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=12017&indexList=%s' % (index)

        email_text = 'A course (%s) that you were watching looks open. Its index number is %s. Click the link below to register for it!\n\n %s \n\n If you don\'t get in, visit this URL: \n\n %s \n\n to continue watching it.\n\n Send any feedback to sniper@rutgers.io' % (course, index, register_url, url)

        # send out the email
        message = Message('[Course Sniper](%s) is open' %(course), sender=EMAIL_SENDER)
        message.body = email_text
        message.add_recipient(snipe.user.email)
        message.add_recipient(snipe.user.email)

        mail.send(message)

    db.session.delete(snipe)
    db.session.commit()

    app.logger.warning('Notified user: %s about snipe %s' % (snipe.user, snipe))



if __name__ == '__main__':
    # get all the courses that should be queried.
    app.logger.warning("----------- Running the Cron %s " % (str(datetime.datetime.now())))
    subjects = db.session.query(Snipe.subject).distinct().all()
    for subject in subjects:
        poll(subject[0])
