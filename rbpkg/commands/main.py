from __future__ import unicode_literals

import argparse
import logging
import sys

import pkg_resources

from rbpkg import get_version_string


logger = logging.getLogger(__name__)


def _get_command(command_name):
    """Return the command class for a given name.

    Args:
        command_name (unicode):
            The name of the command.

    Returns:
        rbpkg.commands.base.BaseCommand:
        The command class, or ``None`` if a command could not be found.
    """
    ep = pkg_resources.get_entry_info('rbpkg', 'rbpkg_commands',
                                      command_name)

    if ep:
        try:
            return ep.load()()
        except Exception:
            logger.exception(
                'There was an internal error loading the command "%s".',
                ep.name)
            sys.exit(1)

    return None


def _iter_command_entrypoints():
    """Generate all entrypoints for all registered commands.

    Returns:
        generator:
        The generator for iterating through all entry points.
    """
    return pkg_resources.iter_entry_points('rbpkg_commands')


def _build_help_text(command):
    """Return help text from a command.

    Args:
        command (rbpkg.commands.base.BaseCommand):
            The command.

    Returns:
        unicode:
        The help text.
    """
    parser = command.setup_options()

    return parser.format_help()


def _show_help(args, parser):
    """Display help for rbpkg or a rbpkg command.

    If a command is specified, it will be loaded, and help text displayed from
    the command class. Otherwise, the main rbpkg help text will be shown, and
    all commands listed.

    Once help has been displayed, rbpkg will exit.

    Args:
        args (list):
            The positional arguments passed on the command line.

        parser (argparse.ArgumentParser):
            The argument parser.
    """
    if args:
        command_name = args[0]
        command = _get_command(command_name)

        if command:
            help_text = _build_help_text(command)
            print(help_text)
            sys.exit(0)

        print('No help found for %s' % command_name)
        sys.exit(0)

    parser.print_help()

    print('\nCommands:')

    for ep in _iter_command_entrypoints():
        print('  %s' % ep.name)

    sys.exit(0)


def main():
    """Execute a rbpkg command.

    The registered console script will call this when executing
    :command:`rbpkg`. This will locate the appropriate command and execute it.
    """
    parser = argparse.ArgumentParser(
        prog='rbpkg',
        usage='%(prog)s [--version] <command> [options] [<args>]',
        add_help=False)

    parser.add_argument('-v', '--version',
                        action='version',
                        version='rbpkg %s' % get_version_string())
    parser.add_argument('-h', '--help',
                        action='store_true',
                        dest='help',
                        default=False)
    parser.add_argument('command',
                        nargs=argparse.REMAINDER,
                        help='The command to execute, and any arguments. '
                             '(See below.)')

    opt = parser.parse_args()

    if not opt.command:
        _show_help([], parser)

    command_name = opt.command[0]
    args = opt.command[1:]

    if command_name == 'help':
        _show_help(args, parser)
    elif opt.help or '--help' in args or '-h' in args:
        _show_help(opt.command, parser)

    # Attempt to retrieve the command class from the entry points.
    command = _get_command(command_name)

    if command:
        command.run_from_argv(args)
    else:
        parser.error('"%s" is not a valid command.' % command_name)
