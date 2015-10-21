from __future__ import unicode_literals

import dateutil.parser
from six.moves.urllib.parse import urljoin

from rbpkg.api.package_bundle import PackageBundle


FORMAT_VERSION = '1.0'


class PackageIndex(object):
    """An index of core packages in the repository.

    The index will contain the core set of packages that rbpkg should directly
    track. It won't necessarily contain all packages in the repository,
    however.

    The entries in the index will provide enough information for rbpkg to
    quickly check whether it has the latest version of the core packages,
    and to match those with system-installed packages.

    Attributes:
        manifest_url (unicode):
            The URL to the manifest file. This may be absolute or relative.

        last_updated_timestamp (datetime.datetime):
            The date/time when this package index was last updated.
    """

    @classmethod
    def deserialize(cls, manifest_url, data):
        """Deserialize a payload into a PackageIndex.

        Args:
            manifest_url (unicode):
                The URL to the manifest file being deserialized.

            data (dict):
                The JSON dictionary data for the package bundle definition.

        Returns:
            PackageIndex:
            The resulting package index.
        """
        index = PackageIndex(
            manifest_url=manifest_url,
            last_updated_timestamp=dateutil.parser.parse(
                data['last_updated_timestamp']))

        base_url = urljoin(manifest_url, '.')

        index.bundles = [
            PackageBundle.deserialize(
                base_url=base_url,
                manifest_url=bundle_data['manifest_file'],
                data=bundle_data)
            for bundle_data in data['bundles']
        ]

        return index

    def __init__(self, manifest_url=None, last_updated_timestamp=None):
        """Initialize the package index.

        Args:
            manifest_url (unicode):
                The URL to the manifest file.

            last_updated_timestamp (datetime.datetime):
                The date/time when this package bundle was last updated.
        """
        self.manifest_url = manifest_url
        self.last_updated_timestamp = last_updated_timestamp
        self.bundles = []

    def serialize(self):
        """Serialize the package index into a JSON-serializable format.

        The resulting output can be written into the package repository once
        further serialized to a JSON file.

        Returns:
            dict:
            The serialized package index data.
        """
        return {
            'format_version': FORMAT_VERSION,
            'last_updated_timestamp': self.last_updated_timestamp.isoformat(),
            'bundles': [
                package_bundle.serialize_index_entry()
                for package_bundle in self.bundles
            ],
        }

    def __repr__(self):
        return '<PackageIndex(%s bundles)>' % len(self.bundles)
