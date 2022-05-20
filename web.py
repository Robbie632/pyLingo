from flask import Flask, render_template, url_for, redirect
from wtforms import Form, BooleanField, TextField, validators, SubmitField
from game import Game
from config import Config

#

from wtforms import Form, TextField

class RegistrationForm(Form):
    user_input = TextField('input')

form = RegistrationForm()

def home():
    return render_template("index.html", form=form, swedish="")

def on_submit():
    print("clicked submit")
    return render_template("index.html", form=form, swedish="")

def on_peek():
    print("peeked")
    return render_template("index.html", form=form, swedish="")

def on_audio():
    print("played audio")
    return render_template("index.html", form=form, swedish="")

def on_skip():
    print("skipped")
    return render_template("index.html", form=form, swedish="")

def on_reset():
    print("reset")
    return render_template("index.html", form=form, swedish="")

def on_update_phrase(swedish):
    return render_template("index.html", form=form, swedish=swedish)


class Web(Game):
    def __init__(self, phrases_category: str, config: Config):
        Game.__init__(self, phrases_category, config)
        self.app = Flask(__name__)
        self.add_endpoint('/', 'one', home)
        self.add_endpoint('/', "submit", on_submit)
        self.add_endpoint('/', "skip", on_skip)
        self.add_endpoint('/', "audio", on_audio)
        self.add_endpoint('/', "peek", on_peek)
        self.add_endpoint('/', "reset", on_reset)
        self.add_endpoint('/<swedish>', "on_update_phrase", on_update_phrase)
        self.load_phrases()
        self.load_weights()
        self.initialise_category()
        self.new_phrase()

    def add_endpoint(self, endpoint, endpoint_name, func):
        self.app.add_url_rule(endpoint, endpoint_name, func)

    def run(self):
        self.app.run()

    def on_submit(self):
        on_submit()

    def on_audio(self):
        on_audio()

    def on_skip(self):
        on_skip()

    def on_reset(self):
        on_reset()

    def on_peek(self):
        on_peek()

    def initialise_category(self):
        pass

    def update_phrase(self, message: str):
        with self.app.app_context():
            return redirect(url_for(on_update_phrase, message=message))




if __name__ == '__main__':
    config_path = 'config.json'
    phrases_category = "conversational"
    config = Config(config_path)
    w = Web(phrases_category, config)
    w.run()