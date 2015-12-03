from __future__ import unicode_literals

import pkg_resources
import six

from rbpkg.package_manager.dep_graph import DependencyGraph
from rbpkg.package_manager.errors import (DependencyConflictError,
                                          PackageInstallError)
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_repo import get_repository
from rbpkg.utils.matches import matches_version_range


class PendingInstall(object):
    """A pending install of one or more packages.

    This tracks the packages the caller has requested to install, along with
    any dependencies referenced by those packages or by other dependencies.

    All required dependencies will be automatically included in the install.
    Recommended and optional dependencies may also be included, if requested.

    Callers are expected to add one or more packages using
    :py:meth:`add_package`. Once all packages have been added, dependencies
    must be resolved using :py:meth:`resolve_dependencies`. The resulting
    install order of packages can then be retrieved using
    :py:meth:`get_install_order`.
    """

    #: Install all required dependencies. This is the default.
    INSTALL_DEPS_REQUIRED = 0

    #: Install all required and recommended dependencies.
    INSTALL_DEPS_RECOMMENDED = 1

    #: Install all required, recommended, and optional dependencies.
    INSTALL_DEPS_ALL = 2

    def __init__(self, install_deps_mode=INSTALL_DEPS_REQUIRED):
        """Initialize the PendingInstall.

        Args:
            install_deps_mode (int):
                The mode used for determining which types of dependencies
                will be installed. This can be one of
                :py:attr:`INSTALL_DEPS_REQUIRED` (default),
                :py:attr:`INSTALL_DEPS_RECOMMENDED`, or
                :py:attr:`INSTALL_DEPS_ALL`.
        """
        self.install_deps_mode = install_deps_mode

        self._bundle_infos = []
        self._bundle_infos_map = {}
        self._dep_graph = DependencyGraph()
        self._repository = get_repository()

    def add_package(self, release, package_type):
        """Add a package to be installed.

        The desired release and package type must be specified. These will be
        checked to ensure that there's a package compatible with this system
        and package type.

        Args:
            release (rbpkg.repository.package_release.PackageRelease):
                The release to install.

            package_type (unicode):
                The desired package type to install.

        Raises:
            rbpkg.package_manager.errors.PackageInstallError:
                Error installing the package, due to a compatibility issue
                or lack of install rules for the version. The error message
                will provide additional details.
        """
        bundle = release.channel.bundle
        all_rules = release.channel.get_all_rules_for_version(release.version)

        if not all_rules:
            raise PackageInstallError(
                '"%s" could not be installed on this system.'
                % bundle.name)

        # Find the first set of rules matching the requested package type.
        rules = None
        available_package_types = set()

        for temp_rules in all_rules:
            available_package_types.add(temp_rules.package_type)

            if not package_type or temp_rules.package_type == package_type:
                rules = temp_rules
                break

        if not rules:
            assert package_type

            raise PackageInstallError(
                '"%s" is not available as a "%s" package. Choices are: %s'
                % (bundle.name, package_type,
                   ', '.join(sorted(available_package_types))))

        bundle_info = {
            'bundle': bundle,
            'release': release,
            'package_type': package_type,
            'rules': rules,
        }
        self._bundle_infos.append(bundle_info)
        self._bundle_infos_map[bundle.name] = bundle_info

    def get_install_order(self):
        """Return the install order for packages.

        This will provide the list of package bundle information to install, in
        the necessary order. It must be called after all packages have been
        added and all dependencies resolved.

        Returns:
            list of dict:
            The list of package bundle information, in the order in which they
            should be installed.
        """
        return [
            self._bundle_infos_map[name]
            for name in self._dep_graph.iter_sorted()
        ]

    def resolve_dependencies(self):
        """Resolve all dependencies for packages.

        This will look up any dependencies for the added packages, fetch them,
        validate them, and then add them to the list of packages to install.

        When processing a dependency's package bundle, only release channels
        will be considered, unless the bundle requesting the dependency is
        from a pre-release channel. This means that a stable release of a
        package will never install a pre-release dependency, but a pre-release
        of a package will.

        This must be called after adding packages, and before fetching the
        install order.

        Raises:
            rbpkg.package_manager.errors.DependencyConflictError:
                There was a conflict between two dependencies. Most likely,
                two packages requested two incompatible versions of the same
                dependency. The error message will provide additional details.
        """
        # Save the current list of bundles we've added, in case we have to
        # restore them later.
        prev_bundle_infos = list(self._bundle_infos)
        prev_bundle_infos_map = self._bundle_infos_map.copy()

        try:
            self._resolve_dependencies_for_bundles(self._bundle_infos)
        except:
            # Things went wrong, so restore the state we had before.
            self._bundle_infos = prev_bundle_infos
            self._bundle_infos_map = prev_bundle_infos_map
            self._dep_graph = DependencyGraph()

            raise

    def _resolve_dependencies_for_bundles(self, bundle_infos):
        """Resolve dependencies for a list of bundle information.

        This is a helper function for :py:meth:`resolve_dependencies`, which
        operates on a list of bundle information. It will process the list of
        dependencies for each of those packages, and then the lists for each
        dependency, and so on, recursively.

        Args:
            bundle_infos (list):
                A list of bundle information dictionaries.

        Raises:
            rbpkg.package_manager.errors.DependencyConflictError:
                There was a conflict between two dependencies. Most likely,
                two packages requested two incompatible versions of the same
                dependency. The error message will provide additional details.
        """
        new_bundle_infos = []

        for bundle_info in bundle_infos:
            rules = bundle_info['rules']

            new_bundle_infos.extend(self._process_dependencies_list(
                bundle_info,
                rules.required_dependencies))

            if self.install_deps_mode in (self.INSTALL_DEPS_RECOMMENDED,
                                          self.INSTALL_DEPS_ALL):
                new_bundle_infos.extend(self._process_dependencies_list(
                    bundle_info,
                    rules.recommended_dependencies))

                if self.install_deps_mode == self.INSTALL_DEPS_ALL:
                    new_bundle_infos.extend(self._process_dependencies_list(
                        bundle_info,
                        rules.optional_dependencies))

        if new_bundle_infos:
            self._bundle_infos.extend(new_bundle_infos)
            self._bundle_infos_map.update(
                (bundle_info['bundle'].name, bundle_info)
                for bundle_info in new_bundle_infos
            )

            self._resolve_dependencies_for_bundles(new_bundle_infos)

    def _process_dependencies_list(self, bundle_info, deps):
        """Process a single list of dependencies for a bundle.

        This is a helper function for
        :py:meth:`_resolve_dependencies_for_bundles`, which does the hard
        work of checking for version conflicts, looking up a dependency's
        package bundle, and adding the information on the package for later
        installation.

        Args:
            bundle_info (dict):
                The bundle information containing the bundle owning this
                list of dependencies.

            deps (list of unicode):
                The list of dependencies to process.

        Raises:
            rbpkg.package_manager.errors.DependencyConflictError:
                There was a conflict between two dependencies. Most likely,
                two packages requested two incompatible versions of the same
                dependency. The error message will provide additional details.
        """
        for dep in deps:
            dep_name, dep_version_range = self._split_dependency(dep)

            if dep_name in self._bundle_infos_map:
                # Something else already depended on this bundle, but it
                # may be an incompatible version. Make sure the version we've
                # already processed matches this version specifier.
                prev_dep_release = self._bundle_infos_map[dep_name]['release']

                if not matches_version_range(prev_dep_release.version, dep):
                    raise DependencyConflictError(
                        'Multiple packages want %s at incompatible versions.'
                        % dep_name)

            # Let any PackageLookupErrors bubble up.
            dep_bundle = self._repository.lookup_package_bundle(dep_name)

            channel_types = set([PackageChannel.CHANNEL_TYPE_RELEASE])
            channel_types.add(bundle_info['release'].channel.channel_type)

            # TODO: Allow channel types to be specified somehow? For now,
            #       default to what's in the bundle.
            dep_release = dep_bundle.get_latest_release_for_version_range(
                dep_version_range,
                channel_types=channel_types)

            dep_rules = dep_release.channel.get_all_rules_for_version(
                dep_release.version)
            assert dep_rules

            self._dep_graph.add(bundle_info['bundle'].name, [dep_bundle.name])

            yield {
                'bundle': dep_bundle,
                'release': dep_release,
                'package_type': None,
                'rules': dep_rules[0],
            }

    def _split_dependency(self, dep):
        req = pkg_resources.Requirement.parse(dep)

        return req.unsafe_name, six.text_type(req.specifier)
