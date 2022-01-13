from os import environ
from app import app

if __name__ == '__main__':
    app.debug = True
    app.env = 'production'
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '8080'))
    except ValueError:
        PORT = 80
    app.run(HOST, PORT)
