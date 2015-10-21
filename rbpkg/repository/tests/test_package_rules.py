from __future__ import unicode_literals

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_rules import PackageRules
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageRulesTests(PackagesTestCase):
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
