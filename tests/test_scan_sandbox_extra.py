"""Extra regression tests for scripts/scan_sandbox.py (drop into tests/).

Each payload below slipped past the previous scanner. The safe cases guard against false positives.
Every case is its own subTest, so one failure does not hide the others.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
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
    ]
    MUST_PASS = [
        "import pandas as pd\npd.read_csv('data/train.csv')",
        "import pandas as pd\npd.DataFrame().to_csv('out.csv', index=False)",
        "import numpy as np\nnp.load('m.npy')",
        "import numpy as np\nnp.load('m.npy', allow_pickle=False)",
        "import matplotlib.pyplot as plt\nplt.savefig('fig.png')",
        "print('Training...')",
    ]

    def test_gaps_are_closed(self):
        for code in self.MUST_CATCH:
            with self.subTest(code=code):
                self.assertTrue(scan_sandbox.scan_code(code, 't.py'), "not caught")

    def test_no_false_positives(self):
        for code in self.MUST_PASS:
            with self.subTest(code=code):
                self.assertEqual(scan_sandbox.scan_code(code, 't.py'), [])


if __name__ == '__main__':
    unittest.main()
