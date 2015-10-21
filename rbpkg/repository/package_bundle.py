from __future__ import unicode_literals

import dateutil.parser
from six.moves.urllib.parse import urljoin

from rbpkg.repository.loaders import get_data_loader
from rbpkg.repository.package_channel import PackageChannel


FORMAT_VERSION = '1.0'


class PackageBundle(object):
    """A stored bundle of types of packages that can be installed or managed.

    This is the starting point for working with any package. From here,
    the various channel can be looked up, and queries on the package
    can be made.

    Attributes:
        manifest_url (unicode):
            The URL to the manifest file. This may be absolute or relative.

        absolute_manifest_url (unicode):
            The absolute URL to the manifest file.

        created_timestamp (datetime.datetime):
            The date/time when this package bundle was first created.

        last_updated_timestamp (datetime.datetime):
            The date/time when this package bundle was last updated.

        name (unicode):
            The name of the package bundle. This is what users will specify
            when installing a package.

        package_names (list):
            A list of possible package names and their package types, based on
            lists of operating systems. This is an aggregated version of what's
            in the channels.

            Each item is a dictionary containing the following data:

            * ``systems``: A list of platform identifiers.
            * ``package_type``: The type of package.
            * ``name``: The package name.

            See the attributes on
            :py:class:`~rbpkg.repository.package_rules.PackageRules` for
            explanations of these values.
    """

    @classmethod
    def deserialize(cls, base_url, manifest_url, data):
        """Deserialize a payload into a PackageBundle.

        This supports both package entries from the packages index, and from
        a full package bundle manifest file. When loading from the index,
        loading additional data will result in fetching the package bundle
        manifest.

        Args:
            base_url (unicode):
                The base URL that ``manifest_url`` may be derived from.

            manifest_url (unicode):
                The URL to the manifest file being deserialized.

            data (dict):
                The JSON dictionary data for the package bundle definition.

        Returns:
            PackageBundle:
            The resulting package bundle.
        """
        bundle = PackageBundle(
            base_url=base_url,
            manifest_url=manifest_url,
            name=data['name'],
            description='\n'.join(data.get('description', [])) or None,
            created_timestamp=dateutil.parser.parse(
                data['created_timestamp']),
            last_updated_timestamp=dateutil.parser.parse(
                data['last_updated_timestamp']),
            current_version=data.get('current_version'),
            channel_aliases=data.get('channel_aliases', {}),
            package_names=data.get('package_names', {}))

        if 'channels' in data:
            # This is a full package payload.
            bundle._channels = [
                PackageChannel.deserialize(bundle, channel_data)
                for channel_data in data['channels']
            ]

            bundle._loaded = True

        return bundle

    def __init__(self, base_url=None, manifest_url=None,
                 created_timestamp=None, last_updated_timestamp=None,
                 name=None, description=None, current_version=None,
                 channel_aliases=None, package_names=None):
        """Initialize the package bundle.

        Args:
            base_url (unicode):
                The base URL that ``manifest_url`` may be derived from.

            manifest_url (unicode):
                The URL to the manifest file.

            created_timestamp (datetime.datetime):
                The date/time when this package bundle was first created.

            last_updated_timestamp (datetime.datetime):
                The date/time when this package bundle was last updated.

            name (unicode):
                The name of the package bundle. This is what users will
                specify when installing a package.

            description (unicode):
                The description of the package bundle. The first line is
                expected to be the package summary, followed by a blank line,
                and then a longer description of the package. All but the
                summary are optional.

            current_version (unicode):
                The current version of the package.

            channel_aliases (dict):
                A mapping of aliases for channel. This is useful for setting
                up channels or providing compatibility when changing the
                version of a set of packages.

            package_names (list):
                A list of information on possible names for the package in
                the local package managers.
        """
        self.manifest_url = manifest_url
        self.absolute_manifest_url = urljoin(base_url, manifest_url)
        self.created_timestamp = created_timestamp
        self.last_updated_timestamp = last_updated_timestamp
        self.name = name
        self.current_version = current_version
        self.package_names = package_names or []
        self._description = description
        self._channel_aliases = channel_aliases or {}
        self._channels = []
        self._loaded = False

    @property
    def description(self):
        """The description of the package bundle.

        The first line is expected to be the package summary, followed by a
        blank line, and then a longer description of the package. All but the
        summary are optional.
        """
        if not self._loaded:
            self.load()

        return self._description

    @property
    def channel_aliases(self):
        """A mapping of aliases for channel.

        This is useful for setting up channels or providing compatibility when
        changing the version of a set of packages.
        """
        if not self._loaded:
            self.load()

        return self._channel_aliases

    @property
    def channels(self):
        """The list of channels for this package bundle."""
        if not self._loaded:
            self.load()

        return self._channels

    def serialize_index_entry(self):
        """Serialize the package bundle for the package index.

        The resulting output can be consumed into a
        :py:class:`~rbpkg.repository.package_index.PackageIndex` payload.

        Returns:
            dict:
            The serialized package bundle data.
        """
        return {
            'created_timestamp': self.created_timestamp.isoformat(),
            'last_updated_timestamp': self.last_updated_timestamp.isoformat(),
            'name': self.name,
            'package_names': self.package_names,
            'manifest_file': self.manifest_url,
            'current_version': self.current_version,
        }

    def serialize(self):
        """Serialize the package bundle into a JSON-serializable format.

        The resulting output can be written into the package repository
        once further serialized to a JSON file.

        Returns:
            dict:
            The serialized package bundle data.
        """
        data = {
            'format_version': FORMAT_VERSION,
            'created_timestamp': self.created_timestamp.isoformat(),
            'last_updated_timestamp': self.last_updated_timestamp.isoformat(),
            'name': self.name,
            'description': self.description.split('\n'),
            'current_version': self.current_version,
            'package_names': self.package_names,
        }

        if self.channel_aliases:
            data['channel_aliases'] = self.channel_aliases

        if self.channels:
            data['channels'] = [
                channel.serialize_package_entry()
                for channel in self.channels
            ]

        return data

    def load(self):
        """Load data from the manifest file.

        The data from the manifest will be loaded and stored in this
        instance, allowing the caller to access it.
        """
        # Let the exceptions bubble up.
        data = get_data_loader().load_by_path(self.absolute_manifest_url)

        self._channels = []
        self._channel_aliases = []

        self.created_timestamp = \
            dateutil.parser.parse(data['created_timestamp'])
        self.last_updated_timestamp = \
            dateutil.parser.parse(data['last_updated_timestamp'])
        self._description = '\n'.join(data.get('description', [])) or None
        self.current_version = self.current_version
        self.package_names = data['package_names']
        self._channel_aliases = data['channel_aliases']

        self._channels = [
            PackageChannel.deserialize(self, channel_data)
            for channel_data in data['channels']
        ]

        self._loaded = True

    def __repr__(self):
        return '<PackageBundle(%s)>' % self.name
