import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import scan_sandbox


class TestSandbox(unittest.TestCase):
    def test_all_bypass_attempts(self):
        bypasses = [
            "e = eval; e('1+1')",
            "import matplotlib; matplotlib.os.system('id')",
            "().__class__.__base__.__subclasses__()",
            "from . import anything",
            "import numpy as np; np.load('m.npy', allow_pickle=True)",
            "import os",
            "import subprocess",
            "import pickle",
            "import socket",
            "from os import system",
            "from subprocess import run",
            "import importlib; importlib.import_module('os')",
            "eval('1+1')",
            "exec('print(1)')",
            "__import__('os')",
            "getattr(__import__('os'), 'system')('id')",
            "open('/etc/passwd').read()",
            "import pandas as pd; pd.read_pickle('m.pkl')",
            "import pandas as pd; pd.to_pickle(m, 'm.pkl')",
            "x = '../secret'",
            "x = '..\\\\secret'",
        ]
        for payload in bypasses:
            v = scan_sandbox.scan_code(payload, "test.py")
            self.assertTrue(len(v) > 0, "Failed to catch: " + payload)

    def test_safe_ml_code(self):
        safe = [
            "import pandas as pd",
            "from sklearn.linear_model import LogisticRegression",
            "model.eval()",
            "print('Training...')",
            "import json",
            "import numpy as np",
            "import xgboost as xgb",
            "from sklearn.model_selection import KFold",
            "import matplotlib.pyplot as plt",
        ]
        for payload in safe:
            v = scan_sandbox.scan_code(payload, "test.py")
            self.assertEqual(len(v), 0, "False positive on: " + payload)


if __name__ == '__main__':
    unittest.main()
