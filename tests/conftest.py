
def ref_file_head():

    ref_file_str = """{
    "common": [
        "{{project_slug}}/__init__.py",
        "{{project_slug}}/log.py",
        "{{project_slug}}/main.py","""
    return ref_file_str.splitlines()
