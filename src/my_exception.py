from pprint import pprint
class MyException(Exception):
    def __init__(self, message: str, payload: dict = None):
        super().__init__(message)
        self.message = message
        self.payload = payload or {}