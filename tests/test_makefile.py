"""Check Makefile parsing (allows selection of sections)

WARNING: use unittest framework, pytest conflicts with test templates:
template/tests/test_*.py ( {{ }} syntax)
or exclude these tests
"""
import unittest
from itertools import chain
import tempfile
from devopstemplate.makefile import MakefileTemplate as MkTemplate


class TestMakefileTemplate(unittest.TestCase):

    def setUp(self):
        self.__test_str_list = ["# this",
                                "#  is a comment",
                                "# --- section 1 --- text",
                                "VAR  = test",
                                " ",
                                "#---  section2   ---",
                                "#--sec3 test---",
                                "# ---section  3---",
                                "",
                                "VAR1=int",
                                "#---test",
                                "VAR2=bool",
                                "#---section2---",
                                "target: dep",
                                "   cmd"]

    def __section_title_list(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
        return [section.title for section in mk_section_list]

    def __section_content_list(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
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
                                            "section 1",
                                            "section2",
                                            "section  3",
                                            "section2"])

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
        self.assertListEqual(sec_content_list[3], self.__test_str_list[7:12])
        self.assertListEqual(sec_content_list[4], self.__test_str_list[12:])

    def test_generate_contents(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
        gen_str_list = MkTemplate.generate(mk_section_list)
        self.assertListEqual(gen_str_list, self.__test_str_list)

    def test_generate_blacklist(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
        section_keyword_blacklist = ["section2"]
        gen_str_list = MkTemplate.generate(mk_section_list,
                                           section_keyword_blacklist)
        expected_str_list = (self.__test_str_list[:5] +
                             self.__test_str_list[7:12])
        self.assertListEqual(gen_str_list, expected_str_list)

    def test_generate_subst(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
        gen_str_list = MkTemplate.generate(mk_section_list,
                                           var_value_dict={"VAR": "value",
                                                           "VAR1": 5})
        expected_str_list = (self.__test_str_list[:3] +
                             ["VAR = value"] +
                             self.__test_str_list[4:9] +
                             ["VAR1 = 5"] +
                             self.__test_str_list[10:])
        self.assertListEqual(gen_str_list, expected_str_list)

    def test_generate_subst_invalidvar(self):
        mk_section_list = MkTemplate.parse(self.__test_str_list)
        gen_str_list = MkTemplate.generate(mk_section_list,
                                           var_value_dict={"VAR3": "value"})
        self.assertListEqual(gen_str_list, self.__test_str_list)

    def test_makefiletemplate(self):
        # Create tmp file
        with tempfile.TemporaryFile("r+") as fh:
            # write test data to tmp file
            fh.write("\n".join(self.__test_str_list))
            # reset file pointer
            fh.seek(0)
            # read contents into MakefileTemplate object
            mktemp = MkTemplate(fh)

        # Create a new tmp file for writing generated Makefile
        with tempfile.TemporaryFile("r+") as fh:
            # Generate according to modifiers and write Makefile
            mktemp.write(fh,
                         section_keyword_blacklist=["section 1"],
                         var_value_dict={"VAR": "value",
                                         "VAR1": 5})
            # Reset file pointer and read results
            fh.seek(0)
            mktemp_str_list = fh.read().splitlines()

        # Compare expected results with generated results
        expected_str_list = (self.__test_str_list[:2] +
                             self.__test_str_list[5:9] +
                             ["VAR1 = 5"] +
                             self.__test_str_list[10:])
        self.assertListEqual(mktemp_str_list, expected_str_list)


if __name__ == "__main__":
    unittest.main()
