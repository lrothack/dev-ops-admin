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
            section_content_list: list of tuples
                [(section_title, section_content_list),...]
                defining the sections of the Makefile. Concatenating the
                section_content_list elements results in the original inputs.
                Note: any lines before the first section will be returned with
                section_title None.
        """
        # Record content lines in ordered dictionary.
        # Whenever a line contains a section title, a new key is added to the
        # dictionary
        section_dict = OrderedDict()
        # Save the current section title for convenience
        # Initialize the dictionary with None key and an empty list value
        # None refers to all lines before the first section
        section_current = None
        section_dict[section_current] = []
        # Regex for detecting a section title in a line
        # Matches variants of '# --- section ---' with different amounts of
        # whitespace. () groups the section title for easy access.
        p_sec = re.compile(r'^#\s*---\s*(.*)\s*---')
        for line in content_list:
            # Match only matches at the *beginning* of the string
            # --> using ^ in the regex would not strictly be necessary
            match = p_sec.match(line)
            # match is None if no match line does not match regex
            if match:
                # Extract section title (0: entire match, 1: first group, ...)
                section_current = match.group(1)
                # Initialize new section
                section_dict[section_current] = [line]
            else:
                # Add line to current section
                section_dict[section_current].append(line)

        return section_dict.items()

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
