"""API for data loaders, which are used for loading data from a repository.

rbpkg is meant to work with data coming from the main package repository,
but isn't hard-coded for that. For testing purposes, we allow for pluggable
data loaders.
"""

from __future__ import unicode_literals

import json
import os

from rbpkg.repository.errors import ConfigurationError, LoadDataError


_data_loader = None


class PackageDataLoader(object):
    """Base class for a data loader."""

    def load_by_path(self, *parts):
        """Load data from the given path within the repository.

        Args:
            *parts (list of unicode):
                The segments of a path within the repository.

        Returns:
            dict: The loaded data from that path, if found.

        Raises:
            rbpkg.repository.errors.ConfigurationError:
                Indicates a problem with the configuration of rbpkg or its
                environment.

            rbpkg.repository.errors.LoadDataError:
                Error loading or parsing data from the path.
        """
        raise NotImplementedError


class FilePackageDataLoader(PackageDataLoader):
    """A data loader that operates on local files.

    This is primarily intended for local development, where it's desirable
    to work off locally-generated files and not the central package
    repository.
    """

    def load_by_path(self, *parts):
        """Load data from the given path within the repository.

        This required that the :env:`RBPKG_FILE_LOADER_ROOT` environment
        variable is set to the location where rbpkg can find the manifest
        files.

        Args:
            *parts (list of unicode):
                The segments of a path within the repository.

        Returns:
            dict: The loaded data from that path, if found.

        Raises:
            rbpkg.api.errors.ConfigurationError:
                Indicates a problem with the configuration of rbpkg or its
                environment.

            rbpkg.api.errors.LoadDataError:
                Error loading or parsing data from the path.
        """
        root = os.environ.get('RBPKG_FILE_LOADER_ROOT', '')

        if not root or not os.path.isdir(root):
            raise ConfigurationError(
                '$RBPKG_FILE_LOADER_ROOT must be set to a valid path when '
                'using FilePackageDataLoader.')

        path = os.path.join(root, self._normalize_path(os.path.join(*parts)))

        if not os.path.exists(path):
            raise LoadDataError(
                'Unable to load "%s". The file could not be found.' % path)

        try:
            with open(path, 'r') as fp:
                return json.loads(fp.read())
        except IOError as e:
            raise LoadDataError('Unable to load "%s": %s' % (path, e))
        except ValueError as e:
            raise LoadDataError('Unable to parse data at "%s": %s' % (path, e))

    def _normalize_path(self, path):
        """Return a normalized version of the given path.

        The path will be converted from a package repository path format
        (using ``/`` as separators) to a native path, and normalized
        to remove all relative path information (like ``..``).

        Args:
            path (unicode):
                The path to normalize.

        Returns:
            unicode: The normalized path.
        """
        return os.path.normpath(os.path.join(*path.split('/')))


class InMemoryPackageDataLoader(PackageDataLoader):
    """A data loader that operates off pre-defined content for paths.

    This is intended for unit tests, to assist in returning pre-computed,
    deserialized values from different paths.
    """

    def __init__(self, path_to_content={}):
        """Initialize the data loader.

        Args:
            path_to_content (dict, optional):
                A mapping of paths to their returned content.
        """
        self.path_to_content = path_to_content

    def load_by_path(self, *parts):
        """Load data from the given path within the repository.

        The paths must match those passed in to the constructor.

        Args:
            *parts (list of unicode):
                The segments of a path within the repository.

        Returns:
            dict: The loaded data from that path, if found.

        Raises:
            rbpkg.api.errors.LoadDataError:
                Error loading or parsing data from the path.
        """
        path = '/'.join(parts)

        try:
            return self.path_to_content[path]
        except KeyError as e:
            raise LoadDataError('Unable to load "%s": %s' % (path, e))


def get_data_loader():
    """Return the data loader for the session.

    If :env:`RBPKG_USE_FILE_LOADER` is set to ``1``, then
    :py:class:`FilePackageDataLoader`` will be used.

    Returns:
        PackageDataLoader: The data loader instance.
    """
    global _data_loader

    if not _data_loader:
        if os.environ.get('RBPKG_USE_FILE_LOADER') == '1':
            _data_loader = FilePackageDataLoader()
        else:
            raise NotImplementedError

    return _data_loader


def set_data_loader(loader):
    """Set the data loader instance to use for the session.

    This is primarily meant for unit tests.

    Args:
        loader (PackageDataLoader):
            The data loader, or ``None`` to unset the loader.
    """
    global _data_loader

    _data_loader = loader
