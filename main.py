import json
from random import choices
import os
from playsound import playsound, PlaysoundException



class Interface:
    """
    Parent class to be inherited by class for interaction with user
    """

    def __init__(self):
        pass

    def intro(self):
        pass

    def ask(self, message: str):
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
        raise NotImplementedError



class CommandLine(Interface):
    """
    class for interacting with user via command line
    """

    def __init__(self):
        Interface.__init__(self)

    def intro(self):
        print("Hotkeys: s: skip, p: peek, c: check probabilities")

    def ask(self, message: str):
        answer = input(message)
        return answer

    def correct(self):
        print("correct")

    def incorrect(self):
        print("not quite... try again")

    def check_weights(self, weights: str):
        print(f"weights are \n {weights}")

    def ask_load_weights(self) -> bool:

        while True:
            answer = input("Would you like to load weights from previous session?:\n [y]es | [n]o")
            if answer.lower() == "y":
                return True
            elif answer.lower() == "n":
                return False
            else:
                print("please enter a valid input")

    def play_phrase(self, filepath: str):
        playsound(filepath)


class GUI(Interface):
    def __init__(self):
        Interface.__init__(self)

    def intro(self):
        pass

    def ask(self, message: str):
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
        raise NotImplementedError



class Config:
    """
    Holds configurations
    """
    def __init__(self, filepath: str):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                self.params = json.load(f)
        else:
            print(f"config file not found at {filepath}")
            raise Exception


class Game:
    """
    Runs the app
    """

    def __init__(self, reward: int, interface: Interface, syntax: list, config: Config):
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
        self.interface.intro()
        load_weights = self.interface.ask_load_weights()
        if load_weights:
            ret = self.load_weights()

        if not load_weights or not ret:
            self.weights = len(self.syntax) * [1]

        next_word = True
        while True:
            if next_word:
                selected_syntax = choices(self.syntax, weights=self.weights)
                selected_index = self.syntax.index(selected_syntax[0])
                language1 = selected_syntax[0][0]
                language2 = selected_syntax[0][1]

            else:
                next_word = True
            tries = 0
            while True:
                self.save_weights()
                answer = self.interface.ask(language1 + ":" + "\n")
                answer = self.preprocess(answer)
                if answer == "s":
                    self.weights[selected_index] += (self.reward * 2)
                    break
                elif answer == "p":
                    print(language2)
                    next_word = False
                    self.weights[selected_index] += self.reward
                    break
                if answer == "c":
                    self.interface.check_weights(str(self.weights))
                    next_word = False
                    break
                if answer == "i":
                    self.supress_warnings = True
                    print("warnings supressed")
                    next_word=False
                    break
                processed_swedish = self.preprocess(language2)
                if answer != processed_swedish and tries < 3:
                    self.weights[selected_index] += self.reward
                    self.interface.incorrect()
                    hint = self.uppercase_incorrect_words(answer, processed_swedish)
                    print(hint)
                    tries = tries + 1
                    continue
                elif answer != language2 and tries == 3:
                    print(f"the answer is:\n {language2} ")
                    tries = 0
                    self.weights[selected_index] += self.reward
                    continue
                else:
                    self.weights[selected_index] = max(1, self.weights[selected_index] - self.reward)
                    self.interface.correct()
                    try:
                        self.interface.play_phrase(f"audio/{str(selected_index)}.mp3")
                    except PlaysoundException as e:
                        if not self.supress_warnings:
                            print("no audio file found for phrase, this can be added in the audio file ,\n press 'i' to supress this warning in the future")
                        else:
                            pass
                    break

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


if __name__ == "__main__":
    with open("phrases.json", "r") as f:
        phrases = json.load(f)

    clt = CommandLine()
    config = Config("config.json")
    myGame = Game(2, clt, phrases["syntax"], config)

    #gui = GUI()

    #myGame = Game(2, gui, phrases["syntaxt"])
    myGame.run()
