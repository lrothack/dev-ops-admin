"""Wrapper around the setuptools pkg_resources package

The module offers convenience function for easily reading strings,
lists of strings, file names and binary stream for files stored in Python
distribution packages.
"""

from importlib import resources
from typing import BinaryIO


def exists(resource_name: str) -> bool:
    """Package resource wrapper for checking if resource exists

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: boolean specifying existence
    """
    resource = resources.files(__package__).joinpath(resource_name)
    return resource.is_file() or resource.is_dir()


def isdir(resource_name: str) -> bool:
    """Package resource wrapper for checking if resource is a directory

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: boolean specifying is resource is directory
    """
    resource = resources.files(__package__).joinpath(resource_name)
    return resource.is_dir()


def filepath(resource_name: str) -> str:
    """Package resource wrapper for obtaining resource filepath

    Attention: resource might have to be copied to a tmp folder in order to
    obtain a path in the file system. Rather work with the resource directly.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: absolute path to the resource in the file system
    """
    with resources.as_file(
        resources.files(__package__).joinpath(resource_name)
    ) as resource_path:
        return str(resource_path)


def string(resource_name: str, encoding: str = "utf-8") -> str:
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
    resource_path = filepath(resource_name)
    with open(resource_path, "r", encoding=encoding) as resource_file:
        content = resource_file.read()
    return content


def string_list(resource_name: str, encoding: str = "utf-8") -> list[str]:
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


def stream(resource_name: str) -> BinaryIO:
    """Package resource wrapper for obtaining file handle in order to read
    resource contents.

    Params:
        resource_name: Relative path to the resource in the package (from the
            package root)
    Returns: file object for reading resource contents in binary mode
    """
    return open(filepath(resource_name), "rb")
