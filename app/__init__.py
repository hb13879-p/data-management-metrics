from flask import Flask, session
from flask_session import Session

from config import Config

app = Flask(__name__)


class PrefixMiddleware(object):

    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix        

    def __call__(self, environ, start_response):

        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            environ['PATH_INFO'] = 'error' # environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
			
app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/DPR')

app.config.from_object(Config)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
from app import routes
