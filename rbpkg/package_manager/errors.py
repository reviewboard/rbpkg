from __future__ import unicode_literals


class DependencyConflictError(Exception):
    """Dependency conflict between two errors."""


class PackageInstallError(Exception):
    """Error installing a package."""
