import os
import sys

# Add the directory containing controller.py to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.config as config
from app.admin import ParserController

path_to_app = config.PATH_TO_APP
print(path_to_app)
controller = ParserController()
controller.parse(True)