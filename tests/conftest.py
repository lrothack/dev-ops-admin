
def ref_file_head():
    ref_file_list = ['include LICENSE',
                     'include README.md']
    return ref_file_list


def ref_template_head(project_slug):
    ref_template_list = [f'"""Top-level import package for {project_slug}"""',
                         f'from {project_slug}.log import LoggerConfig']
    return ref_template_list
