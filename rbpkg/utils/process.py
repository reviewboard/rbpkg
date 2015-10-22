from __future__ import unicode_literals

import logging
import os
import subprocess
import sys

from rbpkg.utils.errors import ExecuteError


def execute(command, show_output=True, shell=False, cwd=None, env={},
            dry_run=False, none_on_error=False):
    """Execute a command and return the output.

    Args:
        show_output (bool):
            If set, the output will also be shown on stdout.

        shell (bool):
            If set, the command will be interpreted as shell commands.

        cwd (unicode):
            The optional current working directory in which to run the
            command.

        env (dict):
            Any additional environment variables to set when executing. Each
            key and value must be a byte string.

        dry_run (bool):
            If set, the execution will be simulated.

        none_on_error (bool):
            If set, and the command fails with an error, ``None`` will be
            returned instead of raising an
            :py:exc:`~rbpkg.utils.errors.ExecuteError`.

    Returns:
        unicode:
        The stdout and stderr output from the command.

    Raises:
        rbpkg.utils.errors.ExecuteError:
            The command failed with a non-0 return code.
    """
    if isinstance(command, list):
        logging.debug('Running: %s', subprocess.list2cmdline(command))
    else:
        logging.debug('Running: %s', command)

    s = ''

    if not dry_run:
        if show_output:
            stderr = sys.stderr
        else:
            stderr = subprocess.PIPE

        new_env = os.environ.copy()

        if env:
            new_env.update(env)

        p = subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=stderr,
                             shell=shell,
                             close_fds=True,
                             cwd=cwd,
                             env=new_env)

        while p.poll() is None:
            for line in p.stdout.readlines():
                s += line

                if show_output:
                    sys.stdout.write(line)
                    sys.stdout.flush()

        rc = p.wait()

        if rc:
            if none_on_error:
                return None
            else:
                raise ExecuteError('Failed to execute command: %s\n%s'
                                   % (command, s))

    return s
