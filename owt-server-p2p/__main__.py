# __main__.py
import sys
import os
currentDir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(currentDir+'/../proto/generated')
from .service import Server

port = '50051'

if __name__ == '__main__':
    Server.run(port)