from __future__ import unicode_literals

import platform

import pkg_resources


def matches_current_system(systems):
    """Return whether the current system matches any of the provided systems.

    This will compare the current operating system or Linux distribution to
    the list of systems provided and see if any of them match.

    The special value of ``*`` always matches.

    Args:
        systems (list):
            A list of systems to match against.

    Returns:
        bool:
        ``True`` if any of the systems match, or ``False`` if none match.
    """
    cur_system_type = platform.system()

    # Get some OS-specific data for later comparison. These will simply be
    # empty strings on other platforms.
    if cur_system_type == 'Linux':
        cur_system_name, cur_version, unused = platform.dist()
    elif cur_system_type == 'Darwin':
        cur_system_name = 'macosx'
        cur_version = platform.mac_ver()[0]
    elif cur_system_type == 'Windows':
        cur_system_name = 'windows'
        cur_version = platform.win32_ver()[1]

    for system in systems:
        if (system == '*' or
            matches_version_range(cur_version, system, cur_system_name)):
            return True

    return False


def matches_version_range(version, version_range, name=None):
    """Return whether a version matches a given range.

    This will compare the version to a range specification, checking if it
    matches. The range must be in the form of ``name[>=]specifier``.

    If ``name`` is specified, then the name will be compared to the one
    listed in the version range as well.

    Args:
        version (unicode):
            The version to compare against the range.

        version_range (unicode):
            The version range.

        name (unicode, optional):
            The optional name to compare against the one in the version
            range.

    Returns:
        bool:
        ``True`` if the version and, optionally, the name matches.
    """
    req = pkg_resources.Requirement.parse(version_range)

    if name and req.project_name != name:
        return False

    return len(list(req.specifier.filter([version]))) > 0
