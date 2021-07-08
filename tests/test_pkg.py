import unittest
import os
import json
import itertools
from conftest import ref_file_head
import devopstemplate.pkg as pkg


class PackageResourcesTest(unittest.TestCase):

    def setUp(self):
        self.__ref_template_index_head = ref_file_head()

    def test_exists(self):
        self.assertTrue(pkg.exists('template.json'))
        self.assertTrue(pkg.exists('template'))
        self.assertFalse(pkg.exists('dummy_file_nonexits'))

    def test_isdir(self):
        self.assertFalse(pkg.isdir('template.json'))
        self.assertTrue(pkg.isdir('template'))

    def test_filepath(self):
        fpath = pkg.filepath('template.json')
        self.assertTrue(os.path.exists(fpath))

    def test_string(self):
        refstr_head = '\n'.join(self.__ref_template_index_head)
        filestr = pkg.string('template/MANIFEST.in')
        filestr_head = filestr[: len(refstr_head)]
        self.assertEqual(filestr_head, refstr_head)

    def test_string_list(self):
        filestr_list = pkg.string_list('template/MANIFEST.in')
        self.assertEqual(filestr_list[:len(self.__ref_template_index_head)],
                         self.__ref_template_index_head)

    def test_stream(self):
        refstr_head = '\n'.join(self.__ref_template_index_head)
        with pkg.stream('template/MANIFEST.in') as fh:
            buffer = fh.read(2)
            b_list = [buffer]
            while buffer:
                buffer = fh.read(2)
                b_list.append(buffer)
        filestr = b''.join(b_list)
        filestr = filestr.decode()
        filestr_head = filestr[: len(refstr_head)]
        self.assertEqual(filestr_head, refstr_head)

    def test_template_json(self):
        with pkg.stream('template.json') as fh:
            template_dict = json.load(fh)
            filestr_list = list(itertools.chain(*template_dict.values()))

        self.assertTrue(pkg.isdir('template'))
        for fpath in filestr_list:
            self.assertTrue(pkg.exists(f'template/{fpath}'))


if __name__ == "__main__":
    unittest.main()
