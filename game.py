import json
import os
from config import Config
from random import choices
from playsound import playsound


class Game:
    """
    Runs the app
    """

    def __init__(self, syntax: list, config: Config):
        self.config = config
        self.reward = self.config.params["reward"]
        self.syntax = syntax
        self.weights = None
        self.supress_warnings=False

    def run(self):

        """
        Runs control loop
        """
        raise NotImplementedError

    def preprocess(self, sentence: str):
        """
        preprocess a sentence
        """
        sentence = sentence.lower()
        sentence = sentence.strip()
        sentence = sentence.replace("-", " ")
        return sentence

    def uppercase_incorrect_words(self, attempt: str, truth: str):
        """
        returns string with incorrect words in uppercase
        """
        out = []
        for a, t in zip(attempt.split(), truth.split()):
            if a != t:
                out.append(a.upper())
            else:
                out.append(a.lower())
        out = " ".join(out)
        return out

    def load_weights(self):
        """
        Loads the weights from json file
        """
        if os.path.exists("weights.json"):
            with open("weights.json", "r") as f:
                self.weights = json.load(f)["weights"]
            return True
        else:
            return False

    def save_weights(self):
        """saves weights to json file"""
        with open("weights.json", "w") as f:
            json.dump({"weights": self.weights}, f)

    def intro(self):
        pass

    def ask(self, message: str) -> str:
        """ask the user a phrase"""
        raise NotImplementedError

    def correct(self):
        """give feedback that input was correct"""
        raise NotImplemented

    def incorrect(self):
        """give feedback that input was incorrect"""
        raise NotImplementedError

    def check_weights(self, weights: str):
        """show user probability distribution being used to
        control picking of next phrase to ask"""
        raise NotImplementedError

    def ask_load_weights(self) -> bool:
        """
        Ask user if they want ot resume using weights from previous session
        """
        raise NotImplementedError

    def play_phrase(self, filepath: str):
        playsound(filepath)

    def give_audio_warning(self):
        raise NotImplementedError

    def choose_phrase(self):
        selected_syntax = choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]

        return selected_index, language1, language2

    def increase_weight(self, index: int):
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        self.weights[index] = max(1, self.weights[index]-self.reward)

