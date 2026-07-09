import sys
import os
with open('main_dirname.txt', 'w') as f:
    f.write(os.path.dirname(os.path.abspath(__file__)))
