from __future__ import unicode_literals

import platform
from datetime import datetime

from kgb import SpyAgency

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_rules import PackageRules
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageRulesTests(SpyAgency, PackagesTestCase):
    """Unit tests for rbpkg.repository.package.PackageRules."""

    def test_deserialize_with_all_info(self):
        """Testing PackageRules.deserialize with all available info"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)
        rules = PackageRules.deserialize(
            channel,
            {
                'version_range': '*',
                'package_type': 'rpm',
                'package_name': 'TestPackage',
                'systems': ['centos', 'macosx'],
                'dependencies': {
                    'required': ['foo'],
                    'recommended': ['bar'],
                    'optional': ['baz'],
                },
                'replaces': ['OldPackage'],
                'pre_install_commands': [
                    'echo pre-install',
                ],
                'install_commands': [
                    'echo install',
                ],
                'post_install_commands': [
                    'echo post-install',
                ],
                'install_flags': [
                    '--with-pie',
                    '--with-ice-cream',
                ],
                'uninstall_commands': [
                    'echo uninstall',
                ],
            })

        self.assertEqual(rules.version_range, '*')
        self.assertEqual(rules.package_type, PackageRules.PACKAGE_TYPE_RPM)
        self.assertEqual(rules.package_name, 'TestPackage')
        self.assertEqual(rules.systems, ['centos', 'macosx'])
        self.assertEqual(rules.required_dependencies, ['foo'])
        self.assertEqual(rules.recommended_dependencies, ['bar'])
        self.assertEqual(rules.optional_dependencies, ['baz'])
        self.assertEqual(rules.replaces, ['OldPackage'])
        self.assertEqual(rules.pre_install_commands, ['echo pre-install'])
        self.assertEqual(rules.install_commands, ['echo install'])
        self.assertEqual(rules.post_install_commands, ['echo post-install'])
        self.assertEqual(rules.install_flags,
                         ['--with-pie', '--with-ice-cream'])
        self.assertEqual(rules.uninstall_commands, ['echo uninstall'])

    def test_deserialize_with_minimum_info(self):
        """Testing PackageRules.deserialize with minimum info"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)
        rules = PackageRules.deserialize(
            channel,
            {
                'version_range': '*',
                'package_type': 'rpm',
                'systems': ['centos', 'macosx'],
            })

        self.assertEqual(rules.version_range, '*')
        self.assertEqual(rules.package_type, PackageRules.PACKAGE_TYPE_RPM)
        self.assertEqual(rules.systems, ['centos', 'macosx'])
        self.assertEqual(rules.package_name, None)
        self.assertEqual(rules.required_dependencies, [])
        self.assertEqual(rules.recommended_dependencies, [])
        self.assertEqual(rules.optional_dependencies, [])
        self.assertEqual(rules.replaces, [])
        self.assertEqual(rules.pre_install_commands, [])
        self.assertEqual(rules.install_commands, [])
        self.assertEqual(rules.post_install_commands, [])
        self.assertEqual(rules.install_flags, [])
        self.assertEqual(rules.uninstall_commands, [])

    def test_serialize(self):
        """Testing PackageRules.serialize"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)

        rules = PackageRules(
            channel=channel,
            version_range='*',
            package_type=PackageRules.PACKAGE_TYPE_RPM,
            systems=['centos', 'macosx'],
            package_name='TestPackage',
            required_dependencies=['foo'],
            recommended_dependencies=['bar'],
            optional_dependencies=['baz'],
            replaces=['OldPackage'],
            pre_install_commands=['echo pre-install'],
            install_commands=['echo install'],
            post_install_commands=['echo post-install'],
            install_flags=['--with-pie', '--with-ice-cream'],
            uninstall_commands=['echo uninstall'])

        self.assertEqual(
            rules.serialize(),
            {
                'version_range': '*',
                'package_type': 'rpm',
                'package_name': 'TestPackage',
                'systems': ['centos', 'macosx'],
                'dependencies': {
                    'required': ['foo'],
                    'recommended': ['bar'],
                    'optional': ['baz'],
                },
                'replaces': ['OldPackage'],
                'pre_install_commands': [
                    'echo pre-install',
                ],
                'install_commands': [
                    'echo install',
                ],
                'post_install_commands': [
                    'echo post-install',
                ],
                'install_flags': [
                    '--with-pie',
                    '--with-ice-cream',
                ],
                'uninstall_commands': [
                    'echo uninstall',
                ],
            })

    def test_matches_version_with_wildcard(self):
        """Testing PackageRules.matches_version with wildcard (*)"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='*',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['*'])
        channel._package_rules = [rules]

        self.assertTrue(rules.matches_version('1.0',
                                              require_current_system=False))

    def test_matches_version_with_exact_version(self):
        """Testing PackageRules.matches_version with exact version"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='1.0',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['*'])
        channel._package_rules = [rules]

        self.assertTrue(rules.matches_version('1.0',
                                              require_current_system=False))

    def test_matches_version_with_range(self):
        """Testing PackageRules.matches_version with version range"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='>=1.0,<=2.0',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['*'])
        channel._package_rules = [rules]

        self.assertTrue(rules.matches_version('1.0',
                                              require_current_system=False))

    def test_matches_version_without_match(self):
        """Testing PackageRules.matches_version without match"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='>=2.0',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['*'])
        channel._package_rules = [rules]

        self.assertFalse(rules.matches_version('1.0',
                                               require_current_system=False))

    def test_matches_version_with_require_current_system_match(self):
        """Testing PackageRules.matches_version with
        require_current_system=True
        """
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='*',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['MyDistro>=1.2.3'])
        channel._package_rules = [rules]

        self.spy_on(platform.system, call_fake=lambda: 'Linux')
        self.spy_on(platform.dist, call_fake=lambda: ('MyDistro', '1.3', ''))

        self.assertTrue(rules.matches_version('1.0',
                                              require_current_system=True))

    def test_matches_version_with_require_current_system_no_match(self):
        """Testing PackageRules.matches_version with
        require_current_system=True and no match
        """
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules = PackageRules(channel=channel,
                             version_range='*',
                             package_type='python',
                             package_name='TestPackage',
                             systems=['MyDistro>=2.3.4'])
        channel._package_rules = [rules]

        self.spy_on(platform.system, call_fake=lambda: 'Linux')
        self.spy_on(platform.dist, call_fake=lambda: ('MyDistro', '1.3', ''))

        self.assertFalse(rules.matches_version('1.0',
                                               require_current_system=True))
