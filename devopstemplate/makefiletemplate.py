import re


class MakefileSection(object):
    """Represents a section of a Makefile

    Attributes:
        title: (declared) title of the section, string or None. None for the
            first section that contains lines not belonging to any explicitly
            declared section.
        content_list: list of strings representing the lines of the section
    """

    def __init__(self, section_title, first_line=None):
        """Initialize section with title and optional first line

        Params:
            section_title: string or None
            first_list: string (without line break) or None. Represents first
                text line of section (title). content_list will be empty
                if None.
        """
        self.title = section_title
        self.content_list = []
        if first_line is not None:
            self.content_list.append(first_line)

    def append_line(self, line):
        """Add a line to the content_list of this section

        Params:
            line: string representing a text line (without line break)
        """
        self.content_list.append(line)


class MakefileTemplate(object):

    # def __init__(self, filepath):
    #     with open(filepath, 'r') as fh:
    #         content_list = fh.readlines()

    #     content_list = [line.strip() for line in content_list]
    #     self.__mk_section_list = self.parse(content_list)

    def parse(self, content_list):
        """Parse the Makefile template and return Makefile divided in sections.

        The first section is a pseudo-section which contains all lines found
        before the first section which is declared in the Makefile. Its section
        title is None (object) and its contents may be represented by an empty
        list if no such lines have been found.

        Params:
            contents_list: list of strings specifying the Makefile template
                contents such that each list element corresponds to a line.
        Returns:
            mk_section_list: list of MakefileSection objects
                defining the sections of the Makefile. Concatenating the
                content_list elements results in the original inputs.
                Note: any lines before the first declared section will be
                returned with section_title None.
        """
        # Record content lines in list of (section, content_line_list).
        # Whenever a line contains a section title, a new item is added to the
        # list
        mk_section_list = []
        # Initialize the list with None section (and an empty list,
        # see MakefileSection class)
        # None refers to all lines before the first section
        mk_section = MakefileSection(section_title=None)
        mk_section_list.append(mk_section)
        # Regex for detecting a section title in a line
        # Matches variants of '# --- section ---' with different amounts of
        # whitespace. () groups the section title for easy access.
        p_sec = re.compile(r'^#\s*---\s*(.*?)\s*---')
        for line in content_list:
            # Match only matches at the *beginning* of the string
            # --> using ^ in the regex would not strictly be necessary
            match = p_sec.match(line)
            # match is None if no match line does not match regex
            if match:
                # Extract section title (0: entire match, 1: first group, ...)
                section_title = match.group(1)
                # Initialize new section
                mk_section = MakefileSection(section_title, first_line=line)
                mk_section_list.append(mk_section)
            else:
                # Add line to current section.
                # --> current section is last element of mk_section_list
                mk_section_list[-1].append_line(line)

        return mk_section_list

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
