from interface import Interface
import json
from config import Config
class Game:
    """
    Runs the app
    """

    def __init__(self, interface: Interface, syntax: list, config: Config):
        self.config = config
        self.reward = self.config.params["reward"]
        self.interface = interface
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