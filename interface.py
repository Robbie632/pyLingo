class Interface:
    """
    Parent class to be inherited by class for interaction with user
    """

    def __init__(self):
        pass

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