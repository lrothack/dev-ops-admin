import unittest
import devopstemplate
from devopstemplate.template import DevOpsTemplate


class TestDevOpsTemplate(unittest.TestCase):

    def test_version(self):
        version = devopstemplate.__version__
        print(f'version: {version}')
        ver_parts = version.split('.')
        self.assertEqual(len(ver_parts), 3)
        for part in ver_parts:
            self.assertGreaterEqual(int(part), 0)


if __name__ == "__main__":
    unittest.main()
