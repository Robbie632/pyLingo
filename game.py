import json
import os
from config import Config
from random import choices
from playsound import playsound


class Game:
    """
    Super class to be implemented and methods not
    implemented should be overrided
    """

    def __init__(self, phrases_category: str, config: Config):
        self.config = config
        self.reward = self.config.params["reward"]
        self.weights = None
        self.supress_warnings=False
        self.syntax = None
        self.phrases_category = phrases_category

    def run(self):

        """
        Runs control loop, listens for events and reacts
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

    def replace_accents(self, sentence):
        """
        replace letters in sentence containing non-primary
        language accents with primary language equivalents
        """
        accents_lookup = self.config.params["accents-lookup"]
        for k, v in accents_lookup.items():
            sentence = sentence.replace(k, v)
        return sentence

    def uppercase_incorrect_words(self, attempt: str, truth: str):
        """
        returns string with incorrect words in uppercase
        """
        out = []
        for a, t in zip(attempt.split(), truth.split()):
            if a != self.replace_accents(t):
                out.append(a.upper())
            else:
                out.append(t.lower())
        out = " ".join(out)
        return out

    def load_weights(self):
        """
        Loads the weights from json file
        """
        path = os.path.join("assets", self.phrases_category, "weights.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                self.weights = json.load(f)["weights"]
            return True
        else:
            return False

    def save_weights(self):
        """saves weights to json file"""
        path = os.path.join("assets", self.phrases_category, "weights.json")
        with open(path, "w") as f:
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
        """
        Plays audio file
        filepath: filepath to mp3 file
        """
        playsound(filepath)

    def give_audio_warning(self):
        """
        Give warning if audio file not found
        """
        raise NotImplementedError

    def load_phrases(self):
        path = os.path.join("assets", self.phrases_category, "phrases.json")

        with open(path, "r") as f:
            self.syntax = json.load(f)["syntax"]

    def choose_phrase(self) -> (int, str, str):
        """
        Chooses phrase to test with
        """
        selected_syntax = choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]

        return selected_index, language1, language2

    def increase_weight(self, index: int):
        """
        increase value of weights at index i
        """
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        """
        increase value of weights at index i
        """
        self.weights[index] = max(1, self.weights[index]-self.reward)

    def reset_weights(self):
        """
        reset weights to all 1 and write new weights to file
        """
        raise NotImplementedError

    def polar_plot(self):
        """
        plot polar plot of weights
        """
        raise NotImplementedError

