from pprint import pprint
class MyLogger:
    @staticmethod
    def log_error(message: str, payload: dict = None):
        print(f"Error: {message}")
        if payload:
            print(f"Payload: ")
            pprint(payload)