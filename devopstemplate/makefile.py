"""Parse and generate a Makefile
- divide Makefile in sections
- combine sections according to user request to new Makefile
"""
import re


class MakefileSection():
    """Represents a section of a Makefile

    Attributes:
        title: (Declared) title of the section, string or None. None for the
            first section that contains lines not belonging to any explicitly
            declared section.
        content_list: List of strings representing the lines of the section
    """

    def __init__(self, section_title, first_line=None):
        """Initialize section with title and optional first line

        Params:
            section_title: String or None
            first_list: String (without line break) or None. Represents first
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
            line: String representing a text line (without line break)
        """
        self.content_list.append(line)


class MakefileTemplate():
    """Parse Makefile template into sections and generate Makefile for project.
    """

    def __init__(self, filehandle):
        # Read file contents and split text lines such that lines are not
        # terminated by 'newline' anymore.
        content_list = filehandle.read().splitlines()
        self.__mk_section_list = self.parse(content_list)

    def write(self, filehandle, section_keyword_blacklist=None,
              var_value_dict=None):
        """Generate and write Makefile *without* contents of specified sections

        See 'generate' method for detailed description (method and parameters).

        Params:
            filehandle: File object that the Makefile will be written to.
            section_keyword_blacklist: List of strings with keywords for
                filtering sections by their titles. (optional)
            var_value_dict: Dict mapping from variable names to variable
                values. (optional)
        """
        content_list = self.generate(self.__mk_section_list,
                                     section_keyword_blacklist,
                                     var_value_dict)
        filehandle.write('\n'.join(content_list))

    @staticmethod
    def parse(content_list):
        """Parse the Makefile template and return Makefile divided in sections.

        The first section is a pseudo-section which contains all lines found
        before the first section which is declared in the Makefile. Its section
        title is None (object) and its contents may be represented by an empty
        list if no such lines have been found.

        Params:
            content_list: List of strings specifying the Makefile template
                contents such that each list element corresponds to a line.
        Returns:
            mk_section_list: List of MakefileSection objects
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

    @staticmethod
    def generate(mk_section_list, section_keyword_blacklist=None,
                 var_value_dict=None):
        """Generate Makefile *without* contents of specified sections

        A section will not be included if a keyword from the
        section_keyword_blacklist is contained in a section title.
        Existing variable assignments can optionally be modified with
        variable_value_dict.

        Params:
            mk_section_list: List of MakefileSection objects. First element
                refers to pseudo-section (section title is None) containing
                lines in front of the first section declaration.
            section_keyword_blacklist: List of strings with keywords for
                filtering sections by their titles. (optional)
            var_value_dict: Dict mapping from variable names to variable
                values. Existing variable assignments will be modified if a
                line begins with the variable name and is followed by any
                Makefile assignment operator. In this case the entire line will
                be replaced with the new variable-value assignment. (optional)

        Returns:
            content_list: List of strings with the generated Makefile template
                contents such that each list element corresponds to a line.
        """
        if section_keyword_blacklist is None:
            keyword_set = set()
        else:
            keyword_set = set(kw.lower() for kw in section_keyword_blacklist)

        if var_value_dict is None:
            var_value_dict = {}

        content_list = []
        # add all lines that have been found before the first declared section
        sec_cont_list = mk_section_list[0].content_list
        # substitute variable assignments
        sub_list = MakefileTemplate.__subst_var_assign(sec_cont_list,
                                                       var_value_dict)
        content_list.extend(sub_list)

        # start with the second element, i.e., with declared section
        for section in mk_section_list[1:]:
            # Check if any keyword from the blacklist is in the section title
            title = section.title.lower()
            if any(kw in title for kw in keyword_set):
                continue

            # Add the section contents to the content_list
            sec_cont_list = section.content_list
            # substitute variable assignments
            sub_list = MakefileTemplate.__subst_var_assign(sec_cont_list,
                                                           var_value_dict)
            content_list.extend(sub_list)

        return content_list

    @staticmethod
    def __subst_var_assign(content_list, variable_value_dict):
        """Substitute variable assignments in content_list

        Params:
            content_list: List of strings representing lines
            variable_value_dict: Dict mapping from variable names to variable
                values. Also see 'generate' method.
        Returns:
            content_subst_list: List of strings, with adjusted assignments.
        """
        # New list for storing processed lines
        content_subst_list = []
        # For each line
        for line in content_list:
            # and all variable-value mappings
            for variable, value in variable_value_dict.items():
                # check if any variable assignment is present at the beginning
                # of the line
                if re.match(r'^%s\s*=' % variable, line):
                    # if so, generate a new line and break the loop as the
                    # current line cannot match with any other variable
                    line = f'{variable} = {value}'
                    break
            # add the processed line to the result list
            content_subst_list.append(line)

        return content_subst_list
