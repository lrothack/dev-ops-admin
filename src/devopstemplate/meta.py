"""Extracts project meta information based on command-line interface."""

import argparse
import importlib.metadata
import logging
import pathlib
import platform
import sys
from typing import Any

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

LOGGER = logging.getLogger(__name__)


class DistributionNotFoundError(ValueError):
    """Indicates that the distribution installed in the current working directory could
    not be retrieved. This is likely due to one of the following reasons:

    - No distribution has been installed in the current working directory.
    - More than one distribution could be found in the context of the current working
      directory.
    """


class OrderedStoreTrueAction(argparse.Action):
    """Defines argparse action which behaves like store_true and saves the order
    of all OrderedStoreTrueActions which have been provided in the command-line
    in an additional tuple: '__optargs_order', see `OrderedStoreTrueAction.ARGS_NS_KEY`.

    Note: the tuple is only available if any of the OrderedStoreTrueActions has been
    provided.

    Usage
    -----
    >>> parser.add_argument(
    >>>     "--name",
    >>>     action=OrderedStoreTrueAction,
    >>>     help="...",
    >>> )
    >>> parser.add_argument(
    >>>     "--version",
    >>>     action=OrderedStoreTrueAction,
    >>>     help="...",
    >>> )

    >>> args_ns = parser.parse_args(["--version", "--name", "--version"])

    >>> if args_ns.name or args_ns.version:
    >>>     for opt_arg in getattr(args_ns, OrderedStoreTrueAction.ARGS_NS_KEY):
    >>>         # process OrderedStoreTrueAction arguments in the order that they
    >>>         # have been provided on the command-line
    >>>         if opt_arg == "name":
    >>>             ...
    >>>         if opt_arg == "version":
    >>>             ...
    """

    ARGS_NS_KEY = "__optargs_order"

    def __init__(
        self,
        option_strings: list[str],
        dest: str,
        nargs: int | None = None,
        const: bool | None = None,
        default: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Arguments are forwarded to super class, after checking for argument usage
        that is compatible with a store_true action.

        Parameters
        ----------
        see `argparse.Action.__init__`
        """
        if nargs is not None:
            raise ValueError("nargs not allowed")
        if const is not None:
            raise ValueError("const not allowed")
        if default is not None:
            raise ValueError("default not allowed")
        super().__init__(
            option_strings,
            dest,
            nargs=0,
            const=True,
            default=False,
            **kwargs,
        )

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        """Register the command-line argument in the namespace object.

        The namespace object will be the result of parsing arguments on the
        command-line, see `argparse.ArgumentParser.parse_args`

        Parameters
        ----------
        see `argparse.ArgumentParser.__call__`
        """
        if self.ARGS_NS_KEY not in namespace:
            setattr(namespace, self.ARGS_NS_KEY, [])
        previous = getattr(namespace, self.ARGS_NS_KEY)
        previous.append(self.dest)
        setattr(namespace, self.ARGS_NS_KEY, previous)
        setattr(namespace, self.dest, self.const)


def parse_args(args_list: list[str] | None) -> argparse.Namespace:
    """Parse command-line arguments

    Parameters
    ----------
    args_list
        List of strings with command-line flags (sys.argv[1:])

    Returns
    -------
    Object storing command-line arguments as attributes and values
    """
    description = "".join(
        (
            "Parse Python application name and its version from the Python ",
            "distribution that is defined within the project's egg.info directory",
        )
    )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--egginfo-path",
        default="./src",
        help="Relative path (wrt project directory) to project's egg.info directory",
    )
    parser.add_argument(
        "--name",
        action=OrderedStoreTrueAction,
        help="Print the name of the Python application to stdout",
    )
    parser.add_argument(
        "--version",
        action=OrderedStoreTrueAction,
        help="Print the version of the Python application to stdout",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only log warning/error messages",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log debug messages",
    )

    # Parse arguments in order to obtain results in argparse.Namespace object
    args_ns = parser.parse_args(args_list)

    # Set log level according to command-line flags
    if args_ns.verbose:
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.debug("%s:: %s\n", platform.node(), " ".join(sys.argv))
    elif args_ns.quiet:
        LOGGER.setLevel(logging.FATAL)

    return args_ns


def distribution_name(egginfo_path: str) -> str:
    """Returns the name of the Python distribution that is defined in the current
    working directory.

    Raises
    ------
    DistributionNotFoundError
        If no or more than one Python distribution have been found in the current
        working directory.
    """
    distribution_name_list: list[str] = []
    search_path = pathlib.Path.cwd() / egginfo_path
    for dist in importlib.metadata.distributions():
        dist_path = pathlib.Path(dist.locate_file(""))  # type: ignore
        LOGGER.debug(dist_path)
        if search_path.resolve() == dist_path.resolve():
            distribution_name_list.append(dist.name)
    if len(distribution_name_list) == 1:
        return distribution_name_list[0]
    raise DistributionNotFoundError(
        "Could not determine distribution name. "
        f"Distributions: {distribution_name_list}"
    )


def distribution_version(_distribution_name: str) -> str:
    """Returns the version that is stored along with the give Python distribution."""
    return importlib.metadata.version(_distribution_name)


def main(args_list: list[str] | None = None) -> None:
    """Entry point for the command-line interface"""
    if args_list is None:
        args_list = sys.argv[1:]
    args_ns = parse_args(args_list)
    LOGGER.debug(args_ns)
    # Start application according to parsing result in args_ns

    if args_ns.name or args_ns.version:
        try:
            _distribution_name = distribution_name(args_ns.egginfo_path)
            lines: list[str] = []
            for opt_arg in getattr(args_ns, OrderedStoreTrueAction.ARGS_NS_KEY):
                if opt_arg == "name":
                    lines.append(_distribution_name)
                if opt_arg == "version":
                    lines.append(distribution_version(_distribution_name))
            sys.stdout.write("\n".join(lines) + "\n")
        except DistributionNotFoundError as err:
            LOGGER.error(err)


if __name__ == "__main__":
    main()
