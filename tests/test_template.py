import unittest
import os
import tempfile
from pathlib import Path
import devopstemplate
from devopstemplate.template import DevOpsTemplate


class TestDevOpsTemplate(unittest.TestCase):

    def setUp(self):
        self.__ref_template_index_head = ['.gitignore',
                                          '.dockerignore',
                                          'tests/__init__.py']

    def test_version(self):
        version = devopstemplate.__version__
        print(f'version: {version}')
        ver_parts = version.split('.')
        self.assertEqual(len(ver_parts), 3)
        for part in ver_parts:
            self.assertGreaterEqual(int(part), 0)

    def test_copy(self):
        template = DevOpsTemplate()
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_fname = os.path.join(tmpdirname, 'tmp_file')
            template._DevOpsTemplate__copy('template.index', tmp_fname)
            with open(tmp_fname, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_copy_exists(self):
        template = DevOpsTemplate()
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_fname = os.path.join(tmpdirname, 'tmp_file')
            tmp_path = Path(tmp_fname)
            tmp_path.touch()
            with self.assertRaises(FileExistsError):
                template._DevOpsTemplate__copy('template.index', tmp_fname)

    def test_copy_skip(self):
        template = DevOpsTemplate(skip_exists=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_fname = os.path.join(tmpdirname, 'tmp_file')
            tmp_path = Path(tmp_fname)
            tmp_path.touch()
            template._DevOpsTemplate__copy('template.index', tmp_fname)
            with open(tmp_fname, 'r') as tmp_fh:
                contents = tmp_fh.read()
                self.assertEqual(contents, '')

    def test_copy_overwrite(self):
        template = DevOpsTemplate(overwrite_exists=True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_fname = os.path.join(tmpdirname, 'tmp_file')
            tmp_path = Path(tmp_fname)
            tmp_path.touch()
            template._DevOpsTemplate__copy('template.index', tmp_fname)
            with open(tmp_fname, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_copy_pkgexists(self):
        template = DevOpsTemplate(overwrite_exists=True)
        with self.assertRaises(FileNotFoundError):
            template._DevOpsTemplate__copy('non_existing_file', None)


if __name__ == "__main__":
    unittest.main()
