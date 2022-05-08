from flask import Flask, render_template
from wtforms import Form, BooleanField, TextField, validators
from game import Game
from config import Config

#http://wtforms.simplecodes.com/docs/1.0.1/crash_course.html

def action():
    return render_template("index.html")


class Web(Game):
    def __init__(self, phrases_category: str, config: Config):
        Game.__init__(self, phrases_category, config)
        self.app = Flask(__name__)

    def add_endpoint(self, endpoint, endpoint_name, func):
        self.app.add_url_rule(endpoint, endpoint_name, func)

    def run(self):
        self.app.run()


if __name__ == '__main__':

    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)
    w = Web(phrases_category, config)
    w.add_endpoint('/', 'one', action)

    w.run()