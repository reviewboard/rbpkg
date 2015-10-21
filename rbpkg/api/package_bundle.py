from __future__ import unicode_literals

import dateutil.parser

from rbpkg.api.package_channel import PackageChannel


FORMAT_VERSION = '1.0'


class PackageBundle(object):
    """A stored bundle of types of packages that can be installed or managed.

    This is the starting point for working with any package. From here,
    the various channel can be looked up, and queries on the package
    can be made.

    Attributes:
        manifest_url (unicode):
            The URL to the manifest file.

        created_timestamp (datetime.datetime):
            The date/time when this package bundle was first created.

        last_updated_timestamp (datetime.datetime):
            The date/time when this package bundle was last updated.

        name (unicode):
            The name of the package bundle. This is what users will specify
            when installing a package.

        description (unicode):
            The description of the package bundle. The first line is expected
            to be the package summary, followed by a blank line, and then
            a longer description of the package. All but the summary are
            optional.

        channel_aliases (dict):
            A mapping of aliases for channel. This is useful for
            setting up channels or providing compatibility when changing the
            version of a set of packages.

        channels (list of rbpkg.api.package_channel.PackageChannel):
            The list of channel for this package bundle.
    """

    @classmethod
    def deserialize(cls, manifest_url, data):
        """Deserialize a payload into a PackageBundle.

        Args:
            manifest_url (unicode):
                The URL to the manifest file being deserialized.

            data (dict):
                The JSON dictionary data for the package bundle definition.

        Returns:
            PackageBundle:
            The resulting package bundle.
        """
        bundle = PackageBundle(
            manifest_url=manifest_url,
            name=data['name'],
            description='\n'.join(data.get('description', [])) or None,
            created_timestamp=dateutil.parser.parse(
                data['created_timestamp']),
            last_updated_timestamp=dateutil.parser.parse(
                data['last_updated_timestamp']),
            channel_aliases=data.get('channel_aliases', {}))

        bundle.channels = [
            PackageChannel.deserialize(bundle, channel_data)
            for channel_data in data['channels']
        ]

        return bundle

    def __init__(self, manifest_url=None, name=None, description=None,
                 created_timestamp=None, last_updated_timestamp=None,
                 channel_aliases=None):
        """Initialize the package bundle.

        Args:
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

            channel_aliases (dict):
                A mapping of aliases for channel. This is useful for setting
                up channels or providing compatibility when changing the
                version of a set of packages.
        """
        self.manifest_url = manifest_url
        self.created_timestamp = created_timestamp
        self.last_updated_timestamp = last_updated_timestamp
        self.name = name
        self.description = description
        self.channel_aliases = channel_aliases or {}
        self.channels = []

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
        }

        if self.channel_aliases:
            data['channel_aliases'] = self.channel_aliases

        if self.channels:
            data['channels'] = [
                channel.serialize_package_entry()
                for channel in self.channels
            ]

        return data

    def __repr__(self):
        return '<PackageBundle(%s)>' % self.name
