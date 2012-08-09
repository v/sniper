#!/usr/bin/env python

import requests
from models import db, Snipe
from soc import Soc

soc = Soc()

def poll(subject):
    courses = soc.get_courses(subject)

    print "Subject: ", subject
    open_data = {}
    for course in courses:
        course_number = course['courseNumber']
        open_data[course_number] = []
        for section in course['sections']:
            # section is open
            if section['openStatus']:
                if course_number in open_data:
                    open_data[course_number].append(section['number'])

        print 'Course: %s Data: %s' %(course_number, open_data[course_number])

    # all of these courses are open
    open_courses = [course for course, open_sections in open_data.iteritems() if open_sections]

    snipes = Snipe.query.filter(Snipe.course_number.in_(open_courses))
    for snipe in snipes:
        if snipe.section in open_data[snipe.course_number]:
            notify(snipe)

def notify(snipe):
    print snipe

if __name__ == '__main__':
    # get all the courses that should be queried.
    subjects = db.session.query(Snipe.subject).distinct().all()
    for subject in subjects:
        poll(subject)
