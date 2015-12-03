from __future__ import unicode_literals

from rbpkg.package_manager.errors import (DependencyConflictError,
                                          PackageInstallError)
from rbpkg.package_manager.pending_install import PendingInstall
from rbpkg.repository.loaders import InMemoryPackageDataLoader, set_data_loader
from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_release import PackageRelease
from rbpkg.repository.package_rules import PackageRules
from rbpkg.testing.testcases import TestCase


class PendingInstallTests(TestCase):
    """Unit tests for rbpkg.package_manager.manager.PendingInstall."""

    def setUp(self):
        super(PendingInstallTests, self).setUp()

        self.data_loader = InMemoryPackageDataLoader()
        set_data_loader(self.data_loader)

    def tearDown(self):
        super(PendingInstallTests, self).tearDown()

        set_data_loader(None)

    def test_add_package(self):
        """Testing PendingInstall.add_package"""
        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules1 = PackageRules(channel=channel,
                              version_range='*',
                              package_type='rpm',
                              package_name='TestPackage',
                              systems=['*'])
        rules2 = PackageRules(channel=channel,
                              version_range='*',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        channel._package_rules = [rules1, rules2]

        pending_install.add_package(release, 'python')

        self.assertEqual(
            pending_install._bundle_infos,
            [
                {
                    'bundle': bundle,
                    'release': release,
                    'package_type': 'python',
                    'rules': rules2,
                }
            ])

        self.assertEqual(
            pending_install._bundle_infos_map,
            {
                'MyPackage': {
                    'bundle': bundle,
                    'release': release,
                    'package_type': 'python',
                    'rules': rules2,
                }
            })

    def test_add_package_without_available_rules(self):
        """Testing PendingInstall.add_package without available rules"""
        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        self.assertRaises(
            PackageInstallError,
            lambda: pending_install.add_package(release, 'python'))

        self.assertEqual(pending_install._bundle_infos, [])
        self.assertEqual(pending_install._bundle_infos_map, {})

    def test_add_package_without_matching_package_type(self):
        """Testing PendingInstall.add_package without matching package type"""
        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(channel=channel,
                             version_range='*',
                             package_type='rpm',
                             package_name='TestPackage',
                             systems=['*'])
        channel._package_rules = [rules]

        self.assertRaises(
            PackageInstallError,
            lambda: pending_install.add_package(release, 'python'))

        self.assertEqual(pending_install._bundle_infos, [])
        self.assertEqual(pending_install._bundle_infos_map, {})

    def test_resolve_dependencies(self):
        """Testing PendingInstall.resolve_dependencies"""
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            recommended_dependencies=[
                'DepPackage2>=1.0',
            ],
            optional_dependencies=[
                'DepPackage3>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 2)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(len(pending_install._bundle_infos_map), 2)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_recommended_deps(self):
        """Testing PendingInstall.resolve_dependencies with recommended
        dependencies
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
            '/packages/DepPackage2/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage2',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage2/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage2',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = \
            PendingInstall(PendingInstall.INSTALL_DEPS_RECOMMENDED)

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            recommended_dependencies=[
                'DepPackage2>=1.0',
            ],
            optional_dependencies=[
                'DepPackage3>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 3)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(pending_install._bundle_infos[2]['bundle'].name,
                         'DepPackage2')
        self.assertEqual(len(pending_install._bundle_infos_map), 3)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage2' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_all_deps(self):
        """Testing PendingInstall.resolve_dependencies with recommended
        and optional dependencies
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
            '/packages/DepPackage2/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage2',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage2/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage2',
                        'systems': ['*'],
                    },
                ],
            },
            '/packages/DepPackage3/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage3',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage3/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage3',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall(PendingInstall.INSTALL_DEPS_ALL)

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            recommended_dependencies=[
                'DepPackage2>=1.0',
            ],
            optional_dependencies=[
                'DepPackage3>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 4)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(pending_install._bundle_infos[2]['bundle'].name,
                         'DepPackage2')
        self.assertEqual(pending_install._bundle_infos[3]['bundle'].name,
                         'DepPackage3')
        self.assertEqual(len(pending_install._bundle_infos_map), 4)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage2' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage3' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_release_only(self):
        """Testing PendingInstall.resolve_dependencies with considering
        release packages only
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '2.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '2.0',
                        'current': False,
                        'visible': True,
                        'type': 'prerelease',
                        'manifest_file': '2.x.json',
                    },
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'type': 'release',
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/2.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '2.0',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall(PendingInstall.INSTALL_DEPS_ALL)

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 2)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(pending_install._bundle_infos[1]['release'].version,
                         '1.5')
        self.assertEqual(len(pending_install._bundle_infos_map), 2)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_prerelease(self):
        """Testing PendingInstall.resolve_dependencies with considering
        pre-release packages
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '2.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '2.0',
                        'current': False,
                        'visible': True,
                        'type': 'prerelease',
                        'manifest_file': '2.x.json',
                    },
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'type': 'release',
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/2.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '2.0',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall(PendingInstall.INSTALL_DEPS_ALL)

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(
            bundle,
            name='1.0.x',
            channel_type=PackageChannel.CHANNEL_TYPE_PRERELEASE)
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 2)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(pending_install._bundle_infos[1]['release'].version,
                         '2.0')
        self.assertEqual(len(pending_install._bundle_infos_map), 2)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_nested_deps(self):
        """Testing PendingInstall.resolve_dependencies with nested dependencies
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                        'dependencies': {
                            'required': [
                                'DepPackage2>=1.0',
                            ],
                        },
                    },
                ],
            },
            '/packages/DepPackage2/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage2',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage2/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage2',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        pending_install.resolve_dependencies()

        self.assertEqual(len(pending_install._bundle_infos), 3)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(pending_install._bundle_infos[1]['bundle'].name,
                         'DepPackage1')
        self.assertEqual(pending_install._bundle_infos[2]['bundle'].name,
                         'DepPackage2')
        self.assertEqual(len(pending_install._bundle_infos_map), 3)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage1' in pending_install._bundle_infos_map)
        self.assertTrue('DepPackage2' in pending_install._bundle_infos_map)

    def test_resolve_dependencies_with_version_conflicts(self):
        """Testing PendingInstall.resolve_dependencies with version conflicts
        """
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                        'dependencies': {
                            'required': [
                                'DepPackage2>=1.5',
                            ],
                        },
                    },
                ],
            },
            '/packages/DepPackage2/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage2',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage2/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    },
                    {
                        'version': '1.0',
                        'type': 'stable',
                        'visible': True,
                    },
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage2',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
                'DepPackage2>=1.0,<1.5',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')

        self.assertRaises(DependencyConflictError,
                          pending_install.resolve_dependencies)

        self.assertEqual(len(pending_install._bundle_infos), 1)
        self.assertEqual(pending_install._bundle_infos[0]['bundle'].name,
                         'MyPackage')
        self.assertEqual(len(pending_install._bundle_infos_map), 1)
        self.assertTrue('MyPackage' in pending_install._bundle_infos_map)

    def test_get_install_order(self):
        """Testing PendingInstall.get_install_order"""
        self.data_loader.path_to_content.update({
            '/packages/DepPackage1/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage1',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage1/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage1',
                        'systems': ['*'],
                        'dependencies': {
                            'required': [
                                'DepPackage2>=1.5',
                            ],
                        },
                    },
                ],
            },
            '/packages/DepPackage2/index.json': {
                'format_version': '1.0',
                'name': 'DepPackage2',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'current_version': '1.5',
                'channels': [
                    {
                        'name': '1.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '1.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.x.json',
                    },
                ],
            },
            '/packages/DepPackage2/1.x.json': {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.5',
                        'type': 'stable',
                        'visible': True,
                    },
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'DepPackage2',
                        'systems': ['*'],
                    },
                ],
            },
        })

        pending_install = PendingInstall()

        bundle = PackageBundle(name='MyPackage')
        channel = PackageChannel(bundle, name='1.0.x')
        channel._loaded = True
        bundle._channels = [channel]

        release = PackageRelease(channel=channel, version='1.0')
        channel._releases = [release]

        rules = PackageRules(
            channel=channel,
            version_range='*',
            required_dependencies=[
                'DepPackage1>=1.0',
            ],
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules = [rules]

        pending_install.add_package(release, 'python')
        pending_install.resolve_dependencies()

        install_order = pending_install.get_install_order()
        self.assertEqual(len(install_order), 3)
        self.assertEqual(install_order[0]['bundle'].name, 'DepPackage2')
        self.assertEqual(install_order[1]['bundle'].name, 'DepPackage1')
        self.assertEqual(install_order[2]['bundle'].name, 'MyPackage')
