from typing import List, Dict


class CannotGetActionFromServerException(Exception):
    def __init__(self, validation_errors: List[Dict] = None, response: Dict = None, *args):
        self.response = response
        self.validation_errors = validation_errors
        self.msg = f"Got a bad response from server: {self.response}" if self.validation_errors is None \
            else \
                   f"Validation error trying to initialize Action: {self.validation_errors}"
        super().__init__(self.msg, *args)
