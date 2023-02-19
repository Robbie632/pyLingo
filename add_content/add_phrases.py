import json
import os
from PyQt5.QtWidgets import (QMainWindow,
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QVBoxLayout,
                             QAction, QMessageBox, QApplication)


class AddPhraseWindow(QWidget):
    """
    Window for adding new phrase
    """
    def __init__(self, main_window, category):
        super().__init__()
        self.main_window = main_window
        self.category = category
        layout = QVBoxLayout()
        info = QLabel("Add a new line for each phrase, seperate lines with *")
        self.setWindowTitle("pyLingo-phrase addition")
        self.input_box_1 = QTextEdit()
        self.input_box_2 = QTextEdit()
        self.input_box_1.setFixedSize(600, 200)
        self.input_box_2.setFixedSize(600, 200)

        self.submit = QPushButton(self)
        self.submit.setText("submit")
        self.submit.setFixedSize(100, 30)
        self.submit.clicked.connect(self.on_submit)

        self.text1 = QLabel("known phrase(s)")
        self.text2 = QLabel("new language phrase(s)")
        layout.addWidget(info)
        layout.addWidget(self.text1)
        layout.addWidget(self.input_box_1)
        layout.addSpacing(50)
        layout.addWidget(self.text2)
        layout.addWidget(self.input_box_2)
        layout.addSpacing(25)
        layout.addWidget(self.submit)
        self.setFixedSize(800, 800)
        self.setLayout(layout)
        self.key_press_num=0
    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Space:
        #     self.test_method()
        if event.key() == 80:
          self.test_method()
    def test_method(self):
      w = QWidget()

      screen = QApplication.primaryScreen()
      screenshot = screen.grabWindow( self.winId() )
      screenshot.save(f"{self.key_press_num}_add_phrase_screenshot.png", "png")
      self.key_press_num += 1
      w.close()

    def on_submit(self) -> None:
        skip = False
        feedback = QMessageBox()

        syntax = self.load_phrases(self.category)
        mother_tongue_phrases = self.input_box_1.toPlainText().split("*")
        new_language_phrases = self.input_box_2.toPlainText().split("*")

        if len(mother_tongue_phrases) != len(new_language_phrases):
            feedback.setText("please enter the same number of phrases in each box")
        elif mother_tongue_phrases[0] == "" and len(mother_tongue_phrases) == 1:
            feedback.setText("Please enter some text before submitting")

        for mt, nl in zip(mother_tongue_phrases, new_language_phrases):
            # check if phrase already present in app, if it is skip adding it to the syntax
            for mt_nl in syntax["syntax"]:
                if self.main_window.preprocess(mt) == mt_nl[0] or self.main_window.preprocess(nl) == mt_nl[0]:
                    skip = True
            if skip:
                skip = False
                continue
            else:
                syntax["syntax"].append([self.main_window.preprocess(mt), self.main_window.preprocess(nl)])

        self.write_phrases(self.category, syntax)
        self.input_box_1.clear()
        self.input_box_2.clear()
        feedback.setText(f"you have successfully added to the category: {self.category}")
        feedback.exec()

    def load_phrases(self, category: str) -> dict:
        path = os.path.join("assets", category, "phrases.json")

        with open(path, "r") as f:
            syntax = json.load(f)
        return syntax

    def write_phrases(self, category: str, syntax: dict) -> list:
        path = os.path.join("assets", category, "phrases.json")

        with open(path, "w") as f:
            json.dump(syntax, f, indent=4)