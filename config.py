import json
import os
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