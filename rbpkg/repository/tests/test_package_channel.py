from __future__ import unicode_literals

from datetime import datetime

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_release import PackageRelease
from rbpkg.repository.package_rules import PackageRules
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageChannelTests(PackagesTestCase):
    """Unit tests for rbpkg.repository.package.PackageChannel."""

    def test_deserialize_with_all_info(self):
        """Testing PackageChannel.deserialize with all available info"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel.deserialize(
            bundle,
            {
                'name': '1.0.x',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'latest_version': '1.0.0',
                'current': True,
                'visible': False,
                'manifest_file': '1.0.x.json',
            })

        self.assertEqual(channel.name, '1.0.x')
        self.assertEqual(channel.manifest_url, '1.0.x.json')
        self.assertEqual(channel.absolute_manifest_url,
                         'packages/TestPackage/1.0.x.json')
        self.assertEqual(channel.created_timestamp,
                         datetime(2015, 10, 11, 8, 17, 29, 958569))
        self.assertEqual(channel.last_updated_timestamp,
                         datetime(2015, 10, 12, 8, 17, 29, 958569))
        self.assertEqual(channel.latest_version, '1.0.0')
        self.assertTrue(channel.current)
        self.assertFalse(channel.visible)

    def test_serialize_package_entry(self):
        """Testing PackageChannel.serialize_package_entry"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569),
            latest_version='1.0.0',
            current=True,
            visible=True,
            manifest_url='1.0.x.json')

        self.assertEqual(
            channel.serialize_package_entry(),
            {
                'name': '1.0.x',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'latest_version': '1.0.0',
                'current': True,
                'visible': True,
                'manifest_file': '1.0.x.json',
            })

    def test_serialize(self):
        """Testing PackageChannel.serialize"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        release = PackageRelease(
            channel=channel,
            version='1.0',
            release_type=PackageRelease.TYPE_STABLE)
        channel._releases.append(release)

        rules = PackageRules(
            channel=channel,
            version_range='*',
            package_type='python',
            package_name='TestPackage',
            systems=['*'])
        channel._package_rules.append(rules)

        self.assertEqual(
            channel.serialize(),
            {
                'format_version': '1.0',
                'created_timestamp': '2015-10-11T08:17:29.958569',
                'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                'releases': [
                    {
                        'version': '1.0',
                        'type': 'stable',
                        'visible': True,
                    }
                ],
                'package_rules': [
                    {
                        'version_range': '*',
                        'package_type': 'python',
                        'package_name': 'TestPackage',
                        'systems': ['*'],
                    },
                ],
            })

    def test_load(self):
        """Testing PackageChannel.load"""
        self.data_loader.path_to_content['packages/TestPackage/1.0.x.json'] = {
            'format_version': '1.0',
            'created_timestamp': '2015-10-11T08:17:29.958569',
            'last_updated_timestamp': '2015-10-12T08:17:29.958569',
            'releases': [
                {
                    'version': '1.0',
                    'type': 'stable',
                    'visible': True,
                }
            ],
            'package_rules': [
                {
                    'version_range': '*',
                    'package_type': 'python',
                    'package_name': 'TestPackage',
                    'systems': ['*'],
                },
            ],
        }

        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle,
            manifest_url='packages/TestPackage/1.0.x.json')
        channel.load()

        self.assertEqual(channel.created_timestamp,
                         datetime(2015, 10, 11, 8, 17, 29, 958569))
        self.assertEqual(channel.last_updated_timestamp,
                         datetime(2015, 10, 12, 8, 17, 29, 958569))
        self.assertEqual(len(channel.releases), 1)
        self.assertEqual(len(channel.package_rules), 1)
        self.assertEqual(channel.releases[0].version, '1.0')
        self.assertEqual(channel.package_rules[0].package_type,
                         'python')
