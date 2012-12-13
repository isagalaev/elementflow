import sys
import os
import unittest

DIRNAME = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(DIRNAME, 'src'))

def runtests(**kwargs):
    unittest.main(module='tests', argv=' ', **kwargs)

if __name__ == '__main__':
    runtests()
