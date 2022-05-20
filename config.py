import json
import os
class Config:
    """
    Holds configurations
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.params = json.load(f)

        else:
            print(f"config file not found at {self.filepath}")
            raise Exception

    def write_to_file(self):

        with open(self.filepath, "w") as f:
            json.dump(self.params, f, indent=4)
