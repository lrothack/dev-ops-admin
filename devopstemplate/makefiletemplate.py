import re
from collections import OrderedDict


class MakefileTemplate(object):

    def __init__(self):
        pass

    def parse(self, content_list):
        """Parse the Makefile template and return Makefile divided in sections.

        Params:
            contents_list: list of strings specifying the Makefile template
                contents such that each list element corresponds to a line.
        Returns:
            sections: list of tuples [(section_title, section_content),...]
                defining the sections of the Makefile. Concatenating the
                section_content strings results in the original template.
        """
        section_current = None
        section_dict = OrderedDict()
        section_dict['STARTSECTION'] = []
        p_sec = re.compile('^# +--- (.*)? ---')

    def generate(self, section_titles):
        """Generate Makefile with contents for specified sections

        Relies on the class member section_dict for obtaining section contents
        for section titles.

        Params:
            section_titles: list of strings with section titles.
        Returns:
            contents_list: list of strings with the generated Makefile template
                contents such that each list element corresponds to a line.
        """
