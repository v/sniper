# Introduction

[Sniper](http://sniper.vverma.net) is an application that interfaces with the [Rutgers Schedule of Classes](http://sis.rutgers.edu/soc/) and notifies users via email/text when a course opens up.

It uses 
* [Flask](http://flask.pocoo.org) for the application framework
* [SQLAlchemy](http://www.sqlalchemy.org/) for ORM
* [Twilio](http:://twilio.com) for text communication
* [Requests](http://docs.python-requests.org/en/latest/index.html) for interfacing with the Rutgers Schedule of Classes.
* [Flask-mail](http://packages.python.org/flask-mail/) for interfacing with Gmail SMTP servers (for email notifications).

You can check out the [live version](http://sniper.vverma.net) if you want to simply use its functionality
