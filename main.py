import json
import time
from playsound import playsound, PlaysoundException
from random import choices
from game import Game
from config import Config
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QLabel, QTextEdit, QPushButton)

class CLT(Game):
    """
    Runs the app
    """
    def __init__(self, syntax: list, config: Config):
        Game.__init__(self,  syntax, config)

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
            answer = input("Would you like to load weights from previous session?:\n [y]es | [n]o: \n")
            if answer.lower() == "y":
                return True
            elif answer.lower() == "n":
                return False
            else:
                print("please enter a valid input")
    def give_audio_warning(self):
        print("""no audio file found for phrase, this can be added in the audio file ,
        \n press 'i' to supress this warning in the future""")


    def run(self):

        """
        Runs control loop
        """
        self.intro()
        load_weights = self.ask_load_weights()
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
                answer = self.ask(language1 + ":" + "\n")
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
                    self.check_weights(str(self.weights))
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
                    self.incorrect()
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
                    self.decrease_weight(selected_index)
                    self.correct()
                    try:
                        self.play_phrase(f"audio/{str(selected_index)}.mp3")
                    except PlaysoundException as e:
                        if not self.supress_warnings:
                            self.give_audio_warning()
                        else:
                            pass
                    break


class GUI(Game, QMainWindow):
    def __init__(self, syntax: list, config: Config):
        self.app = QApplication([])
        Game.__init__(self,  syntax, config)
        QMainWindow.__init__(self)


        control_button_height = 30
        control_button_length = 100
        horizontal_button_spacer = 10
        control_button_vertical_placement = 300
        self.tries = 0

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

        self.new_phrase()

    def choose_phrase(self):
        selected_syntax = choices(self.syntax, weights=self.weights)
        selected_index = self.syntax.index(selected_syntax[0])
        language1 = selected_syntax[0][0]
        language2 = selected_syntax[0][1]

        return selected_index, language1, language2

    def increase_weight(self, index: int):
        self.weights[index] += self.reward

    def decrease_weight(self, index: int):
        self.weights[index] = max(1, self.save_weights[index]-self.reward)

    def new_phrase(self):
        self.selected_index, self.language1, self.language2 = self.choose_phrase()
        self.update_phrase(self.language1)

    def update_feedback(self, message: str):
        self.feedback.setText(message)

    def update_phrase(self, message: str):
        self.phrase.setText(message)

    def on_peek(self):
        self.update_feedback(self.language2)

    def on_audio(self):
        self.play_phrase(f"audio/{self.selected_index}.mp3")

    def on_skip(self):
        self.new_phrase()

    def on_submit(self):
        answer = self.input_box.toPlainText()
        processed_answer = self.preprocess(answer)

        if processed_answer == self.language2:
            self.correct()
            self.tries = 0
            self.new_phrase()
        elif processed_answer != self.language2 and self.tries == 3:
            self.incorrect()
            time.sleep(1)
            self.update_feedback(self.language2)
            self.tries = 0
        elif processed_answer != self.language2:
            self.incorrect()
            self.tries += 1

    def intro(self):
        pass

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


    def run(self):
        """
        Runs control loop
        """

        load_weights = self.ask_load_weights()
        if load_weights:
            ret = self.load_weights()

        if not load_weights or not ret:
            self.weights = len(self.syntax) * [1]

        self.show()
        self.app.exec()


if __name__ == "__main__":
    with open("phrases.json", "r") as f:
        phrases = json.load(f)

    config = Config("config.json")

    #myGame = cltGame(phrases["syntax"], config)

    myGame = GUI(phrases["syntax"], config)

    myGame.run()
