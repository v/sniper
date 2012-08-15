#!/usr/bin/env python
# This file implements a facade for the Rutgers Schedule of Classes API.

import requests

class Soc:
    def __init__(self, campus='NB', semester='92012', level='U,G'):
        self.base_url = 'http://sis.rutgers.edu/soc'
        self.params = {
            'campus': campus,
            'semester': semester,
            'level': level,
        }

    
    # Queries the given resource (a string) with the given parameters.
    # For example self.query('/api/subjects.json', { 'keyword': 'Computer Science' })
    def query(self, resource, params):
        params.update(self.params)
        
        r = requests.get(self.base_url + resource, params=params) 

        if r.status_code == requests.codes.ok:
            return r.json

        raise Exception('You made an invalid request %s: %s' % (r.status_code, r.text))

    def get_subjects(self, **kwargs):
        return self.query('/subjects.json', params=kwargs)

    def get_courses(self, subject):
        return self.query('/courses.json', params={'subject': subject})

if __name__ == '__main__':
    soc = Soc()
    print soc.get_courses(subject=198)
    import pdb; pdb.set_trace()
