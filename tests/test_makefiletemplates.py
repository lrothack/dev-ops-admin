import unittest
from itertools import chain
from devopstemplate.makefiletemplate import MakefileTemplate


class TestMakefileTemplate(unittest.TestCase):

    def setUp(self):
        self.__test_str_list = ['# this',
                                '#  is a comment',
                                '# --- section 1 --- text',
                                ' VAR = test',
                                ' ',
                                '#---  section2   ---',
                                '#--sec3 test---',
                                '# ---section  3---',
                                '',
                                '#---test',
                                '#---section2---',
                                'target: dep',
                                '   cmd']

    def __section_title_list(self):
        mk_template = MakefileTemplate()
        mk_section_list = mk_template.parse(self.__test_str_list)
        return [section.title for section in mk_section_list]

    def __section_content_list(self):
        mk_template = MakefileTemplate()
        mk_section_list = mk_template.parse(self.__test_str_list)
        return [section.content_list for section in mk_section_list]

    def test_parse_len(self):
        section_list = self.__section_title_list()
        # Check if number of sections in input equals number of sections in
        # output, number of sections in input must be
        # counted manually
        self.assertEqual(len(section_list), 5)

    def test_parse_sections(self):
        section_list = self.__section_title_list()
        self.assertListEqual(section_list, [None,
                                            'section 1',
                                            'section2',
                                            'section  3',
                                            'section2'])

    def test_parse_contents(self):
        section_content_list = self.__section_content_list()
        content_list = list(chain.from_iterable(section_content_list))
        # Check if concatentation of content_lists for sections results in
        # input content list
        self.assertListEqual(content_list, self.__test_str_list)

    def test_parse_section_contents(self):
        sec_content_list = self.__section_content_list()
        # Check content_lists per section
        self.assertListEqual(sec_content_list[0], self.__test_str_list[:2])
        self.assertListEqual(sec_content_list[1], self.__test_str_list[2:5])
        self.assertListEqual(sec_content_list[2], self.__test_str_list[5:7])
        self.assertListEqual(sec_content_list[3], self.__test_str_list[7:10])
        self.assertListEqual(sec_content_list[4], self.__test_str_list[10:])


if __name__ == "__main__":
    unittest.main()