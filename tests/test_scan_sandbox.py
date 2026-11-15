import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import scan_sandbox

class TestSandbox(unittest.TestCase):
    def test_malicious(self):
        cases = [
            "import os", "import subprocess", "import pickle",
            "eval('1+1')", "exec('print(1)')", 
            "e = eval; e('1+1')",
            "import matplotlib; matplotlib.os.system('id')",
            "().__class__.__base__.__subclasses__()",
            "from . import anything",
            "import numpy as np; np.load('m.npy', allow_pickle=True)",
            "bytes.fromhex('2f6574632f706173737764').decode()",
            "x = '../secret'"
        ]
        for c in cases:
            v = scan_sandbox.scan_code(c, "test.py")
            self.assertTrue(len(v) > 0, f"Failed to catch: {c}")

    def test_safe(self):
        cases = [
            "import pandas as pd", 
            "from sklearn.linear_model import LogisticRegression",
            "model.eval()", 
            "print('Training...')", 
            "def foo():\n    \"\"\"Docstring with ... dots\"\"\"\n    pass",
            "import json"
        ]
        for c in cases:
            v = scan_sandbox.scan_code(c, "test.py")
            self.assertEqual(len(v), 0, f"False positive on: {c}")

if __name__ == '__main__':
    unittest.main()
