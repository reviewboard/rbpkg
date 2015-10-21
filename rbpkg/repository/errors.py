from __future__ import unicode_literals


class ConfigurationError(Exception):
    """Error with the configuration of rbpkg or the environment."""


class LoadDataError(IOError):
    """Error loading or parsing data from the repository."""
