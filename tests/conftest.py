def ref_file_head():
    ref_file_list = [
        "# --- Makefile Intro ---",
        "# Makefile for building and testing Python package including code analysis",
        "#  and reporting to SonarQube in a dockerized build environment",
        "#",
        "# Comments: single '#' for ordinary comments, ",
        "#           '## ' indicates text for 'help' target ",
    ]
    return ref_file_list


def ref_template_head(project_slug):
    ref_template_list = [
        f'"""Top-level import package for {project_slug}"""',
        f"from {project_slug}.log import LoggerConfig",
    ]
    return ref_template_list
