from __future__ import unicode_literals


# The version of rbpkg
#
# This is in the format of:
#
#   (Major, Minor, Micro, Patch, alpha/beta/rc/final, Release Number, Released)
#
VERSION = (0, 1, 0, 0, 'alpha', 0, False)


def get_version_string():
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2] or VERSION[3]:
        version += '.%s' % VERSION[2]

    if VERSION[3]:
        version += '.%s' % VERSION[3]

    if VERSION[4] != 'final':
        if VERSION[4] == 'rc':
            version += ' RC%s' % VERSION[5]
        else:
            version += ' %s %s' % (VERSION[4], VERSION[5])

    if not is_release():
        version += ' (dev)'

    return version


def get_package_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])

    if VERSION[2] or VERSION[3]:
        version += '.%s' % VERSION[2]

    if VERSION[3]:
        version += '.%s' % VERSION[3]

    if VERSION[4] != 'final':
        version += '%s%s' % (VERSION[4], VERSION[5])

    return version


def is_release():
    return VERSION[6]


__version_info__ = VERSION[:-1]
__version__ = get_package_version()
