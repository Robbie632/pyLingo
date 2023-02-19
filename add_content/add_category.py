import json
import os

from PyQt5.QtWidgets import (QMainWindow,
                             QLabel, QTextEdit, QPushButton,
                             QWidget, QVBoxLayout,
                             QAction, QMessageBox, QApplication)


class AddCategoryWindow(QWidget):
    """
    Window for adding new phrase
    """
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        self.setWindowTitle("pyLingo-category addition")
        self.input_box_1 = QTextEdit()

        self.input_box_1.setFixedSize(100, 50)

        self.submit = QPushButton(self)
        self.submit.setText("Create")
        self.submit.setFixedSize(100, 30)
        self.submit.clicked.connect(self.on_submit)

        self.text1 = QLabel("category name")

        layout.addWidget(self.text1)
        layout.addWidget(self.input_box_1)
        layout.addWidget(self.submit)
        self.setFixedSize(300, 300)
        self.setLayout(layout)
        self.key_press_num = 0
        
    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Space:
        #     self.test_method()
        if event.key() == 80:
          self.test_method()
        
          

    def test_method(self):
      w = QWidget()

      screen = QApplication.primaryScreen()
      screenshot = screen.grabWindow( self.winId() )
      screenshot.save(f"{self.key_press_num}_add_category_screenshot.png", "png")
      self.key_press_num += 1
      w.close()

    def on_submit(self) -> None:

        feedback = QMessageBox()
        new_category_name = self.input_box_1.toPlainText()
        if os.path.exists(os.path.join("assets", new_category_name)):
            feedback.setText(f"caetgory already exists, please choose another name")
        else:
            os.makedirs(os.path.join("assets", new_category_name, "audio"))
            self.write_phrases(new_category_name, {"syntax":[]})
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
