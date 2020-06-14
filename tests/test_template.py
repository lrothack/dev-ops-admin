import unittest
import os
import tempfile
from pathlib import Path
from tests.conftest import ref_file_head
from devopstemplate.template import DevOpsTemplate


class TestDevOpsTemplate(unittest.TestCase):

    def setUp(self):
        self.__ref_template_index_head = ref_file_head()

    def test_version(self):
        import devopstemplate
        version = devopstemplate.__version__
        print(f'version: {version}')
        ver_parts = version.split('.')
        self.assertEqual(len(ver_parts), 3)
        for part in ver_parts:
            self.assertGreaterEqual(int(part), 0)

    def test_copy(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            tmp_fname = 'tmp_file'
            tmp_fpath = os.path.join(tmpdirname, tmp_fname)
            template._DevOpsTemplate__copy('template.json', tmp_fname)
            with open(tmp_fpath, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_copy_exists(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            with self.assertRaises(FileExistsError):
                template._DevOpsTemplate__copy('template.json', tmp_fname)

    def test_copy_skip(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname,
                                      skip_exists=True)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            template._DevOpsTemplate__copy('template.json', tmp_fname)
            with open(tmp_path, 'r') as tmp_fh:
                contents = tmp_fh.read()
                self.assertEqual(contents, '')

    def test_copy_overwrite(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            template = DevOpsTemplate(projectdirectory=tmpdirname,
                                      overwrite_exists=True)
            tmp_fname = 'tmp_file'
            tmp_path = Path(os.path.join(tmpdirname, tmp_fname))
            tmp_path.touch()
            template._DevOpsTemplate__copy('template.json', tmp_fname)
            with open(tmp_path, 'r') as tmp_fh:
                contents = tmp_fh.read()
                content_list = contents.splitlines()

        self.assertEqual(content_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_copy_pkgexists(self):
        template = DevOpsTemplate()
        with self.assertRaises(FileNotFoundError):
            template._DevOpsTemplate__copy('non_existing_file', None)


if __name__ == "__main__":
    unittest.main()
