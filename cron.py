#!/usr/bin/env python

import requests
from models import db, Snipe, Course, Section

def poll(department):



if __name__ == '__main__':
    # get all the courses that should be queried.
    courses = Course.query.all()
    for course in courses:
        poll(course)
