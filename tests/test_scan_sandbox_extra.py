"""Extra regression tests for scripts/scan_sandbox.py.
Verifies all bypass vectors and ensures fail-closed behavior on missing or empty directories.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import scan_sandbox


class TestScannerGaps(unittest.TestCase):
    MUST_CATCH = [
        "from pandas import read_pickle\nread_pickle('x.pkl')",
        "from pandas import read_pickle as rp",
        "from matplotlib import os",
        "from sklearn.datasets import fetch_openml",
        "import pandas as pd\npd.read_csv('http://evil.example/x.csv')",
        "import pandas as pd\npd.read_csv('/etc/passwd')",
        "import pandas as pd\npd.DataFrame().to_csv('/root/.bashrc')",
        "import matplotlib.pyplot as plt\nplt.savefig('/etc/cron.d/x')",
        "import numpy as np\nflag = True\nnp.load('m.npy', allow_pickle=flag)",
        "import numpy as np\nnp.load('m.npy', **{'allow_pickle': True})",
        # Verified bypass vectors from audit
        "import pandas as pd\npd.eval('1 + 1')",
        "import pandas as pd\ndf = pd.DataFrame({'a': [1]})\ndf.eval('a + 1')",
        "import pandas as pd\ndf = pd.DataFrame({'a': [1]})\ndf.query('a > 0')",
        "import pandas as pd\np = 'data.csv'\npd.read_csv(p)",
        "import pandas as pd\npd.read_csv('/a' + '/b')",
        "from sklearn.datasets import fetch_california_housing",
        "from numpy import *",
        "import numpy as np\nnp.ctypeslib.load_library('lib', '.')",
        "import matplotlib\nmatplotlib.use('module://evil')",
        "import pandas as pd\npd.DataFrame().to_csv('relative_file.csv')",
        "while True:\n    pass",
        "while 1:\n    x = 1",
    ]

    MUST_PASS = [
        "import pandas as pd\npd.read_csv('data/train.csv')",
        "import pandas as pd\npd.DataFrame().to_csv('out/model.csv', index=False)",
        "import pandas as pd\npd.DataFrame().to_csv('sandbox/out/model.csv')",
        "import numpy as np\nnp.load('data/m.npy')",
        "import numpy as np\nnp.load('data/m.npy', allow_pickle=False)",
        "import matplotlib.pyplot as plt\nplt.savefig('out/fig.png')",
        "import optuna\nimport mlflow",
        "while True:\n    break",
        "for i in range(10):\n    pass",
        "print('Training...')",
    ]

    def test_gaps_are_closed(self):
        for code in self.MUST_CATCH:
            with self.subTest(code=code):
                violations = scan_sandbox.scan_code(code, "test.py")
                self.assertTrue(len(violations) > 0, f"Failed to catch: {code}")

    def test_no_false_positives(self):
        for code in self.MUST_PASS:
            with self.subTest(code=code):
                violations = scan_sandbox.scan_code(code, "test.py")
                self.assertEqual(violations, [], f"False positive on: {code}")

    def test_missing_sandbox_dir_fails_closed(self):
        with self.assertRaises(SystemExit) as cm:
            scan_sandbox.main(["/nonexistent_sandbox_path_12345"])
        self.assertEqual(cm.exception.code, 1)

    def test_empty_sandbox_dir_fails_closed(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            with self.assertRaises(SystemExit) as cm:
                scan_sandbox.main([empty_dir])
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
