# __author: linle
# __date: 2019/12/4

import os
import sys


os.system('')
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASEDIR)
from lib import fileoperator

if __name__ == '__main__':
    fileoperator.start()
