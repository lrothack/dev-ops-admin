"""Wrapper around the setuptools pkg_resources package

The module offers convenience function for easily reading strings,
lists of strings, file names and binary stream for files stored in Python
distribution packages.
"""
import pkg_resources


def exists(resource_name):
    """Package resource wrapper for checking if resource exists

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: boolean specifying existence
    """
    return pkg_resources.resource_exists(__package__,
                                         resource_name)


def isdir(resource_name):
    """Package resource wrapper for checking if resource is a directory

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: boolean specifying is resource is directory
    """
    return pkg_resources.resource_isdir(__package__,
                                        resource_name)


def filepath(resource_name):
    """Package resource wrapper for obtaining resource filepath

    Attention: resource might have to be copied to a tmp folder in order to
    obtain a path in the file system. Rather work with the resource directly.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: absolute path to the resource in the file system
    """
    return pkg_resources.resource_filename(__package__,
                                           resource_name)


def string(resource_name, encoding='utf-8'):
    """Package resource wrapper for obtaining resource contents as string.

    Attention: The originally binary string will be interpreted as a text
    string using the given encoding.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root).
        encoding: String defining the encoding for interpreting the binary
            string. None refers to the default encoding (typically UTF-8).
    Returns: contents of of resource interpreted as text string (default
        encoding)
    """
    resource_string = pkg_resources.resource_string(__package__,
                                                    resource_name)
    return resource_string.decode(encoding)


def string_list(resource_name, encoding='utf-8'):
    """Package resource wrapper for obtaining resource contents as list of
    strings.

    The function uses the 'string' method and splits the resulting string
    in lines.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
        encoding: String defining the encoding for interpreting the binary
            string. None refers to the default encoding (typically UTF-8).
    Returns: contents of of resource interpreted as list of text strings
        (default encoding)
    """
    return string(resource_name, encoding).splitlines()


def stream(resource_name):
    """Package resource wrapper for obtaining file handle in order to read
    resource contents.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: file object for reading resource contents in binary mode
    """
    return pkg_resources.resource_stream(__package__,
                                         resource_name)
