import json
import os
from typing import List


class Config:
    """
    Holds configurations
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.params = json.load(f)
            self.params["phrase-categories"] = self.find_categories()

        else:
            print(f"config file not found at {self.filepath}")
            raise Exception

    def find_categories(self) -> List[str]:
        """
        This method returns list of categories supported
        """
        # look in folder assets for folder names
        categories = os.listdir("assets")
        return categories

    def write_to_file(self):

        with open(self.filepath, "w") as f:
            json.dump(self.params, f, indent=4)
