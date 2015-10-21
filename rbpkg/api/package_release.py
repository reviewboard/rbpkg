from __future__ import unicode_literals


class PackageRelease(object):
    """A released version of a package.

    This provides information on the version number, the type of release,
    whether to show this in a list of available versions, and an optional
    URL to release notes.

    Attributes:
        channel (rbpkg.api.package_channel.PackageChannel):
            The channel this release is a part.

        version (unicode):
            The version number.

        release_type (unicode):
            The release type (one of :py:attr:`TYPE_ALPHA`,
            :py:attr:`TYPE_BETA`, :py:attr:`TYPE_RC`, or
            :py:attr:`TYPE_STABLE`).

        visible (bool):
            Whether or not this version will show up in a list of available
            versions.

        release_notes_url (unicode):
            URL to any release notes for the version.
    """

    #: Alpha releases.
    TYPE_ALPHA = 'alpha'

    #: Beta releases.
    TYPE_BETA = 'beta'

    #: Release candidates.
    TYPE_RC = 'rc'

    #: Stable releases.
    TYPE_STABLE = 'stable'

    @classmethod
    def deserialize(cls, channel, data):
        """Deserialize a payload into a PackageRelease.

        The data will come from the package bundle definition. The more
        specific data in the manifest file won't be loaded initially, but
        will automatically be loaded on demand when accessing the list of
        releases or package rules.

        Args:
            package_channel (rbpkg.api.package_channel.PackageChannel):
                The package channel owning this release.

            data (dict):
                The JSON dictionary data for the channel definition.

        Returns:
            PackageRelease:
            The resulting package release.
        """
        return PackageRelease(
            channel=channel,
            version=data['version'],
            release_type=data.get('type', cls.TYPE_STABLE),
            visible=data.get('visible', True),
            release_notes_url=data.get('release_notes_url'))

    def __init__(self, channel, version=None, release_type=None,
                 visible=True, release_notes_url=None):
        """Initialize the release.

        Args:
            channel (rbpkg.api.package_channel.PackageChannel):
                The channel this release is a part of.

            version (unicode):
                The version number.

            release_type (unicode):
                The release type (one of :py:attr:`TYPE_ALPHA`,
                :py:attr:`TYPE_BETA`, :py:attr:`TYPE_RC`, or
                :py:attr:`TYPE_STABLE`).

            visible (bool):
                Whether or not this version will show up in a list of available
                versions.

            release_notes_url (unicode):
                URL to any release notes for the version.
        """
        self.channel = channel
        self.version = version
        self.release_type = release_type
        self.visible = visible
        self.release_notes_url = release_notes_url

    def serialize(self):
        """Serialize the release into a JSON-serializable format.

        The resulting output can be embedded into the channel
        manifest data.

        Returns:
            dict:
            The serialized release data.
        """
        data = {
            'version': self.version,
            'type': self.release_type,
            'visible': self.visible,
        }

        if self.release_notes_url:
            data['release_notes_url'] = self.release_notes_url

        return data

    def __repr__(self):
        return (
            '<PackageRelease(%s; type=%s; visible=%s)>'
            % (self.version, self.release_type, self.visible)
        )
