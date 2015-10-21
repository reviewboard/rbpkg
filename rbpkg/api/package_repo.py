from __future__ import unicode_literals

from rbpkg.api.loaders import get_data_loader
from rbpkg.api.package_bundle import PackageBundle
from rbpkg.api.package_index import PackageIndex


class PackageRepository(object):
    """Interface with packages on the package repository.

    This provides an API to look up and manage packages living on the
    package repository.
    """

    def __init__(self):
        self._package_bundle_cache = {}
        self._index = None

    def get_index(self):
        """Return the root package index from the repository.

        Returns:
            rbpkg.api.package_index.PackageIndex:
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
            package_bundle_data = get_data_loader().load_by_path(path)
            package_bundle = \
                PackageBundle.deserialize(path, package_bundle_data)

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
        return 'packages/%s/index.json' % name

    def _build_package_index_path(self):
        """Build the path to the main package index.

        Returns:
            unicode:
            The path to the main package index within the repository.
        """
        return 'packages/index.json'
