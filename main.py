import json
import time
import os
from random import choices


from playsound import playsound, PlaysoundException
from interface import Interface
from game import Game
from config import Config
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton)


class CommandLine(Interface):
    """
    class for interacting with user via command line
    """

    def __init__(self):
        Interface.__init__(self)

    def intro(self):
        print("Hotkeys: s: skip, p: peek, c: check probabilities")

    def ask(self, message: str) -> str:
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

class cltGame(Game):
    """
    Runs the app
    """
    def __init__(self, interface: Interface, syntax: list, config: Config):
        Game.__init__(self, interface, syntax, config)

    def choose_phrase(self):
        selected_syntax = choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]

        return selected_index, language1, language2

    def increase_weight(self, index: int):
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        self.weights[index] -= self.reward

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
                selected_index, language1, language2 = self.choose_phrase()
            else:
                next_word = True
            tries = 0
            while True:
                self.save_weights()
                answer = self.interface.ask(language1 + ":" + "\n")
                answer = self.preprocess(answer)
                if answer == "s":
                    self.increase_weight(selected_index)

                    break
                elif answer == "p":
                    print(language2)
                    next_word = False
                    self.increase_weight(selected_index)
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
                    self.increase_weight(selected_index)
                    self.interface.incorrect()
                    hint = self.uppercase_incorrect_words(answer, processed_swedish)
                    print(hint)
                    tries = tries + 1
                    continue
                elif answer != language2 and tries == 3:
                    print(f"the answer is:\n {language2} ")
                    tries = 0
                    self.increase_weight(selected_index)
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


class GUI(QMainWindow, Interface):
    def __init__(self):
        QMainWindow.__init__(self)
        Interface.__init__(self)

        control_button_height = 30
        control_button_length = 100
        horizontal_button_spacer = 10
        control_button_vertical_placement = 300
        self.answered = False
        self.answer = None

        self.setWindowTitle("My App")
        self.phrase = QLabel(self)

        self.phrase.setText("swedish phrase")
        self.phrase.move(10, 10)
        self.phrase.setFixedSize(500, 80)

        self.input_box = QTextEdit(self)
        self.input_box.move(10, 100)
        self.input_box.setFixedSize(500, 50)

        self.feedback = QLabel(self)
        self.feedback.setText("feedback")
        self.feedback.move(10, 150)
        self.feedback.setFixedSize(500, 80)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.move(10, 250)
        self.submit.setFixedSize(control_button_length, control_button_height)
        self.submit.clicked.connect(self.on_submit)

        self.p = QPushButton(self)
        self.p.setText("peek")
        self.p.move(10, control_button_vertical_placement)
        self.p.setFixedSize(control_button_length, control_button_height)

        self.s = QPushButton(self)
        self.s.setText("skip")
        self.s.move(10+control_button_length+horizontal_button_spacer, control_button_vertical_placement )
        self.s.setFixedSize(control_button_length, control_button_height)

        self.a = QPushButton(self)
        self.a.setText("audio")
        self.a.move((2*10)+(2*control_button_length)+horizontal_button_spacer, control_button_vertical_placement )
        self.a.setFixedSize(control_button_length, control_button_height)

        self.setMinimumSize(1000, 500)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def on_submit(self):
        self.answer = self.input_box.toPlainText()
        self.answered = True

    def intro(self):
        pass


    def ask(self, message: str):
        """ask the user a phrase"""
        self.update_phrase(message)
        while not self.answered:
            time.sleep(0.05)
        self.answered = False
        return self.answer

    def correct(self):
        """give feedback that input was correct"""
        self.update_feedback("well done, correct")

    def incorrect(self):
        """give feedback that input was incorrect"""
        self.update_feedback("incorrect")

    def check_weights(self, weights: str):
        """show user probability distribution being used to
        control picking of next phrase to ask"""
        raise NotImplementedError

    def ask_load_weights(self) -> bool:
        """
        Ask user if they want ot resume using weights from previous session
        """
        return True


class guiGame(Game):

    def __init__(self, interface: Interface, syntax: list, config: Config):
        Game.__init__(self, interface, syntax, config)

    def run(self):
        pass








if __name__ == "__main__":
    with open("phrases.json", "r") as f:
        phrases = json.load(f)

    clt = CommandLine()
    app = QApplication([])
    gui = GUI()
    gui.show()
    app.exec()

    config = Config("config.json")
    #myGame = cltGame(clt, phrases["syntax"], config)

    myGame = guiGame(gui, phrases["syntaxt"], config)
    myGame.run()
