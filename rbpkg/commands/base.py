from __future__ import unicode_literals

import argparse
import logging
import os
import platform
import sys
import textwrap

from rbpkg import get_version_string


class LogLevelFilter(logging.Filter):
    """Filter log messages of a given level.

    Only log messages that have the specified level will be allowed by
    this filter. This prevents propagation of higher level types to lower
    log handlers.
    """

    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


class BaseCommand(object):
    """Base class for a rbpkg command."""

    def main(self):
        raise NotImplementedError

    def run_from_argv(self, argv):
        """Run the command.

        This will parse any options, initialize logging, and call the
        subclass's main().
        """
        parser = self.setup_options()

        self.options = parser.parse_args(argv)
        self._init_logging(debug=self.options.debug)

        self.main()

    def setup_options(self):
        """Set up options for the command.

        This instantiates an :py:class:`~argparse.ArgumentParser` with the
        standard --debug and --dry-run options. It then calls the subclass's
        :py:meth:`add_options`, which can provide additional options for
        the parser.

        Returns:
            argparse.ArgumentParser:
            The new argument parser.
        """
        parser = argparse.ArgumentParser(
            description=textwrap.dedent('    %s' % self.__doc__),
            formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('-d', '--debug',
                            action='store_true',
                            default=False,
                            help='Displays debug output.')
        parser.add_argument('--dry-run',
                            action='store_true',
                            default=False,
                            help='Simulates all operations.')

        self.add_options(parser)

        return parser

    def add_options(self, parser):
        """Add custom options to the parser.

        Subclasses can override this to add additional options to the
        argument parser.

        Args:
            parser (argparse.ArgumentParser):
                The argument parser to populate.
        """
        pass

    def _init_logging(self, debug=False):
        """Initialize logging.

        This will set up the log handlers for the various log levels.

        Args:
            debug (bool):
                Whether debug messages should be shown.
        """
        root = logging.getLogger()

        if debug:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter('>>> [%(name)s] %(message)s'))
            handler.setLevel(logging.DEBUG)
            handler.addFilter(LogLevelFilter(logging.DEBUG))
            root.addHandler(handler)

            root.setLevel(logging.DEBUG)
        else:
            root.setLevel(logging.INFO)

        # Handler for info messages. We'll treat these like prints.
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        handler.setLevel(logging.INFO)
        handler.addFilter(LogLevelFilter(logging.INFO))
        root.addHandler(handler)

        # Handler for warnings, errors, and criticals. They'll show the
        # level prefix and the message.
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        handler.setLevel(logging.WARNING)
        root.addHandler(handler)

        logging.debug('rbpkg %s', get_version_string())
        logging.debug('Python %s', sys.version)
        logging.debug('Running on %s', platform.platform())
        logging.debug('Current directory = %s', os.getcwd())
        logging.debug('Arguments = %r', sys.argv)
