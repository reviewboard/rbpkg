from __future__ import unicode_literals

import platform
from datetime import datetime

from kgb import SpyAgency

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_release import PackageRelease
from rbpkg.repository.package_rules import PackageRules
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageChannelTests(SpyAgency, PackagesTestCase):
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
            channel_type=PackageChannel.CHANNEL_TYPE_PRERELEASE,
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
                'channel_type': 'prerelease',
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
            manifest_url='1.0.x.json')
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

    def test_latest_release(self):
        """Testing PackageChannel.latest_release"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        release1 = PackageRelease(
            channel=channel,
            version='1.0.1',
            release_type=PackageRelease.TYPE_STABLE)
        release2 = PackageRelease(
            channel=channel,
            version='1.0',
            release_type=PackageRelease.TYPE_STABLE)
        channel._releases = [release1, release2]

        self.assertEqual(channel.latest_release, release1)

    def test_latest_release_with_no_releases(self):
        """Testing PackageChannel.latest_release with no releases"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        self.assertEqual(channel.latest_release, None)

    def test_get_all_rules_for_version(self):
        """Testing PackageChannel.get_all_rules_for_version"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules1 = PackageRules(channel=channel,
                              version_range='*',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        rules2 = PackageRules(channel=channel,
                              version_range='>=1.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        rules3 = PackageRules(channel=channel,
                              version_range='>=1.0,<=2.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        rules4 = PackageRules(channel=channel,
                              version_range='<=2.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        rules5 = PackageRules(channel=channel,
                              version_range='>=4.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        rules6 = PackageRules(channel=channel,
                              version_range='<1.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        channel._package_rules = [
            rules1, rules2, rules3, rules4, rules5, rules6
        ]

        self.assertEqual(
            channel.get_all_rules_for_version('1.0',
                                              require_current_system=False),
            [rules1, rules2, rules3, rules4])

    def test_get_all_rules_for_version_and_current_system(self):
        """Testing PackageChannel.get_all_rules_for_version with
        require_current_system=True
        """
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569))
        channel._loaded = True

        rules1 = PackageRules(channel=channel,
                              version_range='*',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['macosx'])
        rules2 = PackageRules(channel=channel,
                              version_range='>=1.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['windows'])
        rules3 = PackageRules(channel=channel,
                              version_range='>=1.0,<=2.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['MyDistro>1.2'])
        rules4 = PackageRules(channel=channel,
                              version_range='<=2.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['MyDistro'])
        rules5 = PackageRules(channel=channel,
                              version_range='<=2.0',
                              package_type='python',
                              package_name='TestPackage',
                              systems=['*'])
        channel._package_rules = [rules1, rules2, rules3, rules4, rules5]

        self.spy_on(platform.system, call_fake=lambda: 'Linux')
        self.spy_on(platform.dist, call_fake=lambda: ('MyDistro', '1.3', ''))

        self.assertEqual(
            channel.get_all_rules_for_version('1.0',
                                              require_current_system=True),
            [rules3, rules4, rules5])
