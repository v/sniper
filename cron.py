#!/usr/bin/env python
from flaskext.mail import Message, Mail
from twilio.rest import TwilioRestClient

import requests
from models import db, Snipe
from soc import Soc
from app import mail

soc = Soc()

account = "ACd35259f50af04485caaa4c69b779418b"
token = "a918ed53d5c28a74c0abeb911c7f63af"

client = TwilioRestClient(account=account, token=token)

EMAIL_SENDER = "sniper@vverma.net"

def poll(subject):
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
    course = '%s:%s-%s' % (snipe.subject, snipe.course_number, snipe.section)
    text = 'A course (%s) that you were watching looks open. Go register for it! If you don\'t get in, reply back with "%s" and I\'ll continue watching it' % (course, course)

    if snipe.email:

        message = Message('[Course Sniper](%s) is open' %(course), sender=EMAIL_SENDER)
        message.body = text
        message.add_recipient(snipe.email)

        mail.send(message)

    if snipe.phone_number:
        message = client.sms.messages.create(to=snipe.phone_number, from_="+17328527245", body=text)
        

if __name__ == '__main__':
    # get all the courses that should be queried.
    subjects = db.session.query(Snipe.subject).distinct().all()
    for subject in subjects:
        poll(subject)
