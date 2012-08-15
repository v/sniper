#!/var/virtualenvs/sniper/bin/python
from flup.server.fcgi import WSGIServer
from app import app

class ScriptNameStripper(object):
   to_strip = '/sniper.fcgi'

   def __init__(self, app):
       self.app = app

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = ''
       return self.app(environ, start_response)

app = ScriptNameStripper(app)

if __name__ == '__main__':
    WSGIServer(app).run()
