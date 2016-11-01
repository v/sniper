#!/usr/bin/env python
""" This file implements a facade for the Rutgers Schedule of Classes API."""

# Requests is so awesome
import requests

class Soc:
    """ Communicates with Rutgers SOC """
    def __init__(self, campus='NB', semester='12017', level='U,G'):
        """ We always use certain parameters"""
        self.base_url = 'http://sis.rutgers.edu/soc'
        self.params = {
            'campus': campus,
            'semester': semester,
            'level': level,
        }

        # Spoof the user agent for good measure
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.60 Safari/537.1',
        }


    def query(self, resource, params):
        """Queries the given resource (a string) with the given parameters.
        For example self.query('/api/subjects.json', { 'keyword': 'Computer Science' })"""
        params.update(self.params)

        r = requests.get(self.base_url + resource, params=params, headers=self.headers)

        if r.status_code == requests.codes.ok:
            return r.json

        raise Exception('You made an invalid request %s: %s' % (r.status_code, r.text))

    def get_subjects(self, **kwargs):
        """ Gives you a list of subjects (departments) """
        return self.query('/subjects.json', params=kwargs)

    def get_courses(self, subject):
        """ Gives you a list of courses in a department """
        return self.query('/courses.json', params={'subject': subject})

if __name__ == '__main__':
    soc = Soc()
    #print soc.get_courses(subject=198)
    asdf = soc.get_subjects()
    import pdb; pdb.set_trace()
