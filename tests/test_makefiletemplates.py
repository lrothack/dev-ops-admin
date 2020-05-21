import unittest
from devopstemplate.makefiletemplate import MakefileTemplate


class TestMakefileTemplate(unittest.TestCase):

    def test_parse(self):
        test_str_list = ['# this',
                         '#  is a comment',
                         '# --- section 1 --- sdfsd',
                         ' var = test',
                         ' ',
                         '#---  section2   ---',
                         '---sec3 test---',
                         '# ---section  3---']

        mk_template = MakefileTemplate()
        content_list = mk_template.parse(test_str_list)
        print(content_list)
        section_none_list = ['# this',
                             '#  is a comment']
        section_one_list = ['# --- section 1 --- sdfsd',
                            ' var = test',
                            ' ']
        section_two_list = ['#---  section2   ---',
                            '---sec3 test---']
        section_three_list = ['# ---section  3---']


if __name__ == "__main__":
    unittest.main()
