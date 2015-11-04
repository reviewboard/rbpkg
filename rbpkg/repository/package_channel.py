from __future__ import unicode_literals

import dateutil.parser
from six.moves.urllib.parse import urljoin

from rbpkg.repository.loaders import get_data_loader
from rbpkg.repository.package_release import PackageRelease
from rbpkg.repository.package_rules import PackageRules


FORMAT_VERSION = '1.0'


class PackageChannel(object):
    """A channel of releases for a given package.

    A channel is a named container of releases that may represent a specific
    range of versions ("1.0.x", "1.1.x", etc.) or a general set ("beta"),
    though the latter is generally accomplished through aliases in the
    :py:class:`package bundle <rbpkg.repository.bundle.PackageBundle>`.

    Each channel entry further contains all the specific releases that can
    be installed.

    Attributes:
        bundle (rbpkg.repository.bundle.PackageBundle):
            The bundle that owns the channel.

        manifest_url (unicode):
            The URL to the manifest file. This may be absolute or relative.

        absolute_manifest_url (unicode):
            The absolute URL to the manifest file.

        name (unicode):
            The name of the channel.

        created_timestamp (datetime.datetime):
            The date/time when this package bundle was first created.

        last_updated_timestamp (datetime.datetime):
            The date/time when this package bundle was last updated.

        latest_version (unicode):
            The latest visible version in the channel.

        current (bool):
            Whether this is the current channel of releases to install by
            default.

        visible (bool):
            Whether this channel is visible.
    """

    @classmethod
    def deserialize(cls, bundle, data):
        """Deserialize a payload into a PackageChannel.

        The data will come from the package bundle definition. The more
        specific data in the manifest file won't be loaded initially, but
        will automatically be loaded on demand when accessing the list of
        releases or package rules.

        Args:
            bundle (rbpkg.repository.bundle.PackageBundle):
                The package bundle owning this channel.

            data (dict):
                The JSON dictionary data for the channel definition.

        Returns:
            PackageChannel:
            The resulting package channel.
        """
        return PackageChannel(
            bundle=bundle,
            manifest_url=data['manifest_file'],
            name=data['name'],
            created_timestamp=dateutil.parser.parse(data['created_timestamp']),
            last_updated_timestamp=dateutil.parser.parse(
                data['last_updated_timestamp']),
            latest_version=data['latest_version'],
            current=data.get('current', False),
            visible=data.get('visible', True))

    def __init__(self, bundle, manifest_url=None, name=None,
                 created_timestamp=None, last_updated_timestamp=None,
                 latest_version=None, current=False, visible=True):
        """Initialize the channel.

        Args:
            bundle (rbpkg.repository.bundle.PackageBundle):
                The package bundle owning this channel.

            manifest_url (unicode):
                The URL to the manifest file. This may be absolute or relative.

            name (unicode):
                The name of the channel.

            created_timestamp (datetime.datetime):
                The date/time when this package bundle was first created.

            last_updated_timestamp (datetime.datetime):
                The date/time when this package bundle was last updated.

            latest_version (unicode):
                The latest visible version in the channel.

            current (bool):
                Whether this is the current channel of releases to install by
                default.

            visible (bool):
                Whether this channel is visible.
        """
        self.bundle = bundle
        self.manifest_url = manifest_url
        self.absolute_manifest_url = urljoin(bundle.absolute_manifest_url,
                                             manifest_url)
        self.name = name
        self.created_timestamp = created_timestamp
        self.last_updated_timestamp = last_updated_timestamp
        self.latest_version = latest_version
        self.current = current
        self.visible = visible
        self._loaded = False
        self._releases = []
        self._package_rules = []

    @property
    def releases(self):
        """The list of releases in the channel.

        If the channel manifest file hasn't yet been loaded, it will be
        synchronously loaded first.
        """
        if not self._loaded:
            self.load()

        return self._releases

    @property
    def package_rules(self):
        """The list of package rules in the channel.

        If the channel manifest file hasn't yet been loaded, it will be
        synchronously loaded first.
        """
        if not self._loaded:
            self.load()

        return self._package_rules

    @property
    def latest_release(self):
        """Information on the latest release."""
        try:
            return self.releases[0]
        except IndexError:
            return None

    def get_all_rules_for_version(self, version, require_current_system=True):
        """Return lists of rules for the given version.

        By default, the returned rules will only be those that are valid
        for the current system.

        Args:
            version (unicode):
                The version to restrict rules to.

            require_current_system (bool):
                If set, only rules valid for the current system will be
                returned.

        Returns:
            list:
            A list of :py:class:`~rbpkg.repository.package_rules.PackageRules`
            for the given version.
        """
        return [
            rules
            for rules in self.package_rules
            if rules.matches_version(version, require_current_system)
        ]

    def serialize_package_entry(self):
        """Serialize the channel for inclusion in the package bundle.

        The resulting output can be stored in the serialized package bundle
        data as an entry in the channel list.

        Returns:
            dict:
            The serialized channel data.
        """
        return {
            'name': self.name,
            'created_timestamp': self.created_timestamp.isoformat(),
            'last_updated_timestamp': self.last_updated_timestamp.isoformat(),
            'latest_version': self.latest_version,
            'current': self.current,
            'visible': self.visible,
            'manifest_file': self.manifest_url,
        }

    def serialize(self):
        """Serialize the channel into a JSON-serializable format.

        The resulting output can be written into the package repository
        once further serialized to a JSON file.

        Returns:
            dict:
            The serialized channel data.
        """
        return {
            'format_version': FORMAT_VERSION,
            'created_timestamp': self.created_timestamp.isoformat(),
            'last_updated_timestamp': self.last_updated_timestamp.isoformat(),
            'releases': [
                release.serialize()
                for release in self.releases
            ],
            'package_rules': [
                package_rules.serialize()
                for package_rules in self.package_rules
            ],
        }

    def load(self):
        """Load data from the manifest file.

        The data from the manifest will be loaded and stored in this
        instance, allowing the caller to access it.
        """
        # Let the exceptions bubble up.
        data = get_data_loader().load_by_path(self.absolute_manifest_url)

        self._releases = []
        self._package_rules = []

        self.created_timestamp = \
            dateutil.parser.parse(data['created_timestamp'])
        self.last_updated_timestamp = \
            dateutil.parser.parse(data['last_updated_timestamp'])

        self._releases = [
            PackageRelease.deserialize(self, releases_data)
            for releases_data in data['releases']
        ]

        self._package_rules = [
            PackageRules.deserialize(self, rules_data)
            for rules_data in data['package_rules']
        ]

        self._loaded = True

    def __repr__(self):
        return (
            '<PackageChannel(%s; latest_version=%s; current=%s; '
            'visible=%s)>'
            % (self.name, self.latest_version, self.current, self.visible)
        )
