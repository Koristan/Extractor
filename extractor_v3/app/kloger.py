from datetime import datetime
import os.path

class KLoger:
    def __init__(self, log_name) -> None:
        self.log_name = log_name
        self.config_file = f'logs/{self.log_name}.txt'

    def init(self):

        time_now = datetime.now()

        if (os.path.exists(self.config_file) == False):
            with open(self.config_file, 'a') as file:
                print(f'K-LOG FOR USER: {self.log_name}.\n START TIME: D:{time_now.day}; H:{time_now.hour}; M:{time_now.minute}\n', file=file)

    def message(self, message):
        with open(self.config_file, 'a') as file:
            print(message, file=file)