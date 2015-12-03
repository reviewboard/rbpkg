from __future__ import unicode_literals

import six

from rbpkg.repository.errors import LoadDataError, PackageLookupError
from rbpkg.repository.loaders import get_data_loader
from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_index import PackageIndex


_repository = None


class PackageRepository(object):
    """Interface with packages on the package repository.

    This provides an API to look up and manage packages living on the
    package repository.
    """

    BASE_PATH = '/packages/'

    def __init__(self):
        self._package_bundle_cache = {}
        self._index = None

    def clear_caches(self):
        """Clear all caches.

        Any subsequent lookups of packages will re-fetch from the repository.
        """
        self._package_bundle_cache = {}
        self._index = None

    def get_index(self):
        """Return the root package index from the repository.

        Returns:
            rbpkg.repository.package_index.PackageIndex:
            The root package index.
        """
        if not self._index:
            manifest_url = self._build_package_index_path()
            index_data = get_data_loader().load_by_path(manifest_url)
            self._index = PackageIndex.deserialize(manifest_url, index_data)

        return self._index

    def lookup_package_bundle(self, name):
        """Look up a package bundle by name.

        Args:
            name (unicode):
                The name of the package bundle.

        Returns:
            PackageBundle:
            The package bundle, if found, or ``None`` if a bundle with
            that name doesn't exist.
        """
        package_bundle = self._package_bundle_cache.get(name)

        if package_bundle is None:
            path = self._build_package_bundle_path(name)

            try:
                package_bundle_data = get_data_loader().load_by_path(path)
            except LoadDataError as e:
                raise PackageLookupError(six.text_type(e))

            package_bundle = PackageBundle.deserialize(
                base_url=self.BASE_PATH,
                manifest_url=path,
                data=package_bundle_data)

            self._package_bundle_cache[name] = package_bundle

        return package_bundle

    def _build_package_bundle_path(self, name):
        """Build the path to the named package bundle.

        Args:
            name (unicode):
                The name of the package bundle.

        Returns:
            unicode:
            The path to the bundle within the repository.
        """
        return '%s%s/index.json' % (self.BASE_PATH, name)

    def _build_package_index_path(self):
        """Build the path to the main package index.

        Returns:
            unicode:
            The path to the main package index within the repository.
        """
        return '%sindex.json' % self.BASE_PATH


def get_repository():
    """Return the shared instance of the package repository.

    Returns:
        PackageRepository:
        The package repository.
    """
    global _repository

    if not _repository:
        _repository = PackageRepository()

    return _repository
