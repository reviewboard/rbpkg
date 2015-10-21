from __future__ import unicode_literals


class PackageRules(object):
    """A set of rules for installing and managing packages.

    The rules provide rbpkg with the information needed to install or manage
    packages, and to handle non-Python dependencies or to replace packages
    with other alternatives.

    Each rule may match one or more versions by specifying a version range.

    Attributes:
        channel (rbpkg.api.package_channel.PackageChannel):
            The channel this version is a part.

        version_range (unicode):
            The version range that these rules apply to, or ``*`` to match
            all versions.

        package_type (unicode):
            The type of package. Must be one of
            :py:attr:`PACKAGE_TYPE_DEB`, :py:attr:`PACKAGE_TYPE_PYTHON`,
            :py:attr:`PACKAGE_TYPE_RPM`, or :py:attr:`PACKAGE_TYPE_SOURCE`.

        package_name (unicode):
            The name of the package in the package manager.

        systems (list of unicode):
            A list of systems that these rules apply to. The special value
            of ``*`` matches all systems.

            Valid entries are "macosx", "windows", or any Linux distribution
            matching the result of :py:func:`platform.dist`.

        required_dependencies (list of unicode):
            A list of package bundle names that this depends on.

        recommended_dependencies (list of unicode):
            A list of package bundle names that this recommends.

        optional_dependencies (list of unicode):
            A list of package bundle names that are optional dependencies.

        replaces (list of unicode):
            A list of package bundle names that this package replaces.

        pre_install_commands (list of unicode):
            A list of shell commands to perform prior to installation.

        install_commands (list of unicode):
            A list of shell commands to perform for installation. If not
            set, the native package manager for this package type will be
            used to install the given package.

        post_install_commands (list of unicode):
            A list of shell commands to perform after installation.

        install_flags (list of unicode):
            A list of flags to pass to the native package manager.

        uninstall_commands (list of unicode):
            A list of shell commands to perform for uninstallation. If not
            set, the native package manager for this package type will be
            used to uninstall the given package.
    """

    #: Python packages (eggs or wheels).
    PACKAGE_TYPE_PYTHON = 'python'

    #: RPM packages.
    PACKAGE_TYPE_RPM = 'rpm'

    #: Debian packages.
    PACKAGE_TYPE_DEB = 'deb'

    #: Source installs.
    PACKAGE_TYPE_SOURCE = 'source'

    @classmethod
    def deserialize(cls, channel, data):
        """Deserialize a payload into a PackageRules.

        Args:
            channel (rbpkg.api.package_channel.PackageChannel):
                The channel that contains this set of rules.

            data (dict):
                The JSON dictionary data for the rules definitions.

        Returns:
            PackageRules:
            The resulting package rules.
        """
        deps = data.get('dependencies', {})

        return PackageRules(
            channel,
            version_range=data['version_range'],
            package_type=data['package_type'],
            package_name=data.get('package_name'),
            systems=data['systems'],
            required_dependencies=deps.get('required'),
            recommended_dependencies=deps.get('recommended'),
            optional_dependencies=deps.get('optional'),
            replaces=data.get('replaces'),
            pre_install_commands=data.get('pre_install_commands'),
            install_commands=data.get('install_commands'),
            post_install_commands=data.get('post_install_commands'),
            install_flags=data.get('install_flags'),
            uninstall_commands=data.get('uninstall_commands'))

    def __init__(self, channel, version_range=None, package_type=None,
                 package_name=None, systems=[], required_dependencies=[],
                 recommended_dependencies=[], optional_dependencies=[],
                 replaces=[], pre_install_commands=[], install_commands=[],
                 post_install_commands=[], install_flags=[],
                 uninstall_commands=[]):
        """Initialize the package rules.

        Args:
            channel (rbpkg.api.package_channel.PackageChannel):
                The channel that contains this set of rules.

            version_range (unicode):
                The version range that these rules apply to, or ``*`` to match
                all versions.

            package_type (unicode):
                The type of package. Must be one of
                :py:attr:`PACKAGE_TYPE_DEB`, :py:attr:`PACKAGE_TYPE_PYTHON`,
                :py:attr:`PACKAGE_TYPE_RPM`, or :py:attr:`PACKAGE_TYPE_SOURCE`.

            package_name (unicode):
                The name of the package in the package manager.

            systems (list of unicode):
                A list of systems that these rules apply to. The special value
                of ``*`` matches all systems.

                Valid entries are "macosx", "windows", or any Linux
                distribution matching the result of :py:func:`platform.dist`.

            required_dependencies (list of unicode):
                A list of package bundle names that this depends on.

            recommended_dependencies (list of unicode):
                A list of package bundle names that this recommends.

            optional_dependencies (list of unicode):
                A list of package bundle names that are optional dependencies.

            replaces (list of unicode):
                A list of package bundle names that this package replaces.

            pre_install_commands (list of unicode):
                A list of shell commands to perform prior to installation.

            install_commands (list of unicode):
                A list of shell commands to perform for installation. If not
                set, the native package manager for this package type will be
                used to install the given package.

            post_install_commands (list of unicode):
                A list of shell commands to perform after installation.

            install_flags (list of unicode):
                A list of flags to pass to the native package manager.

            uninstall_commands (list of unicode):
                A list of shell commands to perform for uninstallation. If not
                set, the native package manager for this package type will be
                used to uninstall the given package.
        """
        self.channel = channel
        self.version_range = version_range
        self.package_type = package_type
        self.package_name = package_name
        self.systems = systems or []
        self.required_dependencies = required_dependencies or []
        self.recommended_dependencies = recommended_dependencies or []
        self.optional_dependencies = optional_dependencies or []
        self.replaces = replaces or []
        self.pre_install_commands = pre_install_commands or []
        self.install_commands = install_commands or []
        self.post_install_commands = post_install_commands or []
        self.install_flags = install_flags or []
        self.uninstall_commands = uninstall_commands or []

    def serialize(self):
        """Serialize the package rules into a JSON-serializable format.

        The resulting output can be embedded into the channel data.

        Returns:
            dict:
            The serialized package rules data.
        """
        deps = {}

        if self.required_dependencies:
            deps['required'] = self.required_dependencies

        if self.recommended_dependencies:
            deps['recommended'] = self.recommended_dependencies

        if self.optional_dependencies:
            deps['optional'] = self.optional_dependencies

        data = {
            'version_range': self.version_range,
            'package_type': self.package_type,
            'package_name': self.package_name,
            'systems': self.systems,
        }

        if deps:
            data['dependencies'] = deps

        optional_fields = (
            ('replaces', self.replaces),
            ('pre_install_commands', self.pre_install_commands),
            ('install_commands', self.install_commands),
            ('post_install_commands', self.post_install_commands),
            ('install_flags', self.install_flags),
            ('uninstall_commands', self.uninstall_commands),
        )

        for field_name, value in optional_fields:
            if value:
                data[field_name] = value

        return data

    def __repr__(self):
        return (
            '<PackageRules(version_range=%s; package_type=%s; '
            'package_name=%s>'
            % (self.version_range, self.package_type, self.package_name)
        )
