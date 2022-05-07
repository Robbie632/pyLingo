from flask import Flask, Response
from game import Game
from config import Config

#https://stackoverflow.com/questions/40460846/using-flask-inside-class

class EndpointAction:

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action()
        return self.response

def action():
    print("hello world")

class Web(Game):
    def __init__(self, phrases_category: str, config: Config):
        Game.__init__(self, phrases_category, config)
        self.app = Flask(__name__)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))

    def run(self, **kwargs):
        self.app.run(kwargs)


if __name__ == '__main__':

    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)
    w = Web(phrases_category, config)
    w.add_endpoint(endpoint='/ad', endpoint_name='ad', handler=action)

    w.run(debug=True)