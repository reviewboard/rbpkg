from __future__ import unicode_literals

from datetime import datetime

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageBundleTests(PackagesTestCase):
    """Unit tests for rbpkg.repository.package.PackageBundle."""

    def test_deserialize_with_all_info(self):
        """Testing PackageBundle.deserialize with all available info"""
        bundle = PackageBundle.deserialize(
            '/packages/',
            'TestPackage/index.json',
            {
                'format_version': '1.0',
                'name': 'TestPackage',
                'description': [
                    'This is the summary.',
                    '',
                    'This is the multi-line',
                    'description.',
                ],
                'created_timestamp': '2015-10-10T08:17:29.958569',
                'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                'current_version': '1.0.5',
                'package_names': [
                    {
                        'system': ['centos', 'rhel'],
                        'name': 'reviewboard',
                        'type': 'rpm',
                    },
                ],
                'channel_aliases': {
                    'stable': '1.0.x',
                    'beta': '2.0.x',
                },
                'channels': [
                    {
                        'name': '2.0.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '2.0beta1',
                        'current': False,
                        'visible': True,
                        'manifest_file': '2.0.x.json',
                    },
                    {
                        'name': '1.0.x',
                        'created_timestamp': '2015-10-11T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                        'latest_version': '1.0.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.0.x.json',
                    },
                ]
            })

        self.assertEqual(bundle.manifest_url,
                         'TestPackage/index.json')
        self.assertEqual(bundle.absolute_manifest_url,
                         '/packages/TestPackage/index.json')
        self.assertEqual(bundle.name, 'TestPackage')
        self.assertEqual(bundle.description,
                         'This is the summary.\n'
                         '\n'
                         'This is the multi-line\n'
                         'description.')
        self.assertEqual(bundle.current_version, '1.0.5')
        self.assertEqual(bundle.created_timestamp,
                         datetime(2015, 10, 10, 8, 17, 29, 958569))
        self.assertEqual(bundle.last_updated_timestamp,
                         datetime(2015, 10, 15, 8, 17, 29, 958569))
        self.assertEqual(
            bundle.package_names,
            [
                {
                    'system': ['centos', 'rhel'],
                    'name': 'reviewboard',
                    'type': 'rpm',
                },
            ])
        self.assertEqual(
            bundle.channel_aliases,
            {
                'stable': '1.0.x',
                'beta': '2.0.x',
            })

        # The exact details will be compared in a later unit test. Just
        # sanity-check that we have what we expect.
        self.assertEqual(len(bundle.channels), 2)
        self.assertEqual(bundle.channels[0].name, '2.0.x')
        self.assertEqual(bundle.channels[1].name, '1.0.x')

    def test_deserialize_with_minimal_info(self):
        """Testing PackageBundle.deserialize with minimum info"""
        bundle = PackageBundle.deserialize(
            '/packages/',
            'TestPackage/index.json',
            {
                'format_version': '1.0',
                'name': 'TestPackage',
                'created_timestamp': '2015-10-10T08:17:29.958569',
                'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                'channels': [
                    {
                        'name': '2.0.x',
                        'created_timestamp': '2015-10-13T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-14T08:17:29.958569',
                        'latest_version': '2.0beta1',
                        'current': False,
                        'visible': True,
                        'manifest_file': '2.0.x.json',
                    },
                    {
                        'name': '1.0.x',
                        'created_timestamp': '2015-10-11T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                        'latest_version': '1.0.5',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.0.x.json',
                    },
                ]
            })

        self.assertEqual(bundle.manifest_url,
                         'TestPackage/index.json')
        self.assertEqual(bundle.absolute_manifest_url,
                         '/packages/TestPackage/index.json')
        self.assertEqual(bundle.name, 'TestPackage')
        self.assertEqual(bundle.description, None)
        self.assertEqual(bundle.created_timestamp,
                         datetime(2015, 10, 10, 8, 17, 29, 958569))
        self.assertEqual(bundle.last_updated_timestamp,
                         datetime(2015, 10, 15, 8, 17, 29, 958569))
        self.assertEqual(bundle.current_version, None)
        self.assertEqual(bundle.package_names, [])
        self.assertEqual(bundle.channel_aliases, {})

        # The exact details will be compared in a later unit test. Just
        # sanity-check that we have what we expect.
        self.assertEqual(len(bundle.channels), 2)
        self.assertEqual(bundle.channels[0].name, '2.0.x')
        self.assertEqual(bundle.channels[1].name, '1.0.x')

    def test_serialize(self):
        """Testing PackageBundle.serialize"""
        bundle = PackageBundle(
            manifest_url='packages/TestPackage/index.json',
            name='TestPackage',
            description='This is a summary.\n\nThis is a description.',
            created_timestamp=datetime(2015, 10, 10, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 15, 8, 17, 29, 958569),
            current_version='1.0.0',
            channel_aliases={
                'stable': '1.0.x',
                'beta': '2.0.x',
            },
            package_names=[
                {
                    'system': ['centos', 'rhel'],
                    'name': 'reviewboard',
                    'type': 'rpm',
                },
            ])
        bundle._loaded = True

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569),
            latest_version='1.0.0',
            current=True,
            visible=True,
            manifest_url='1.0.x.json')
        bundle._channels = [channel]

        self.assertEqual(
            bundle.serialize(),
            {
                'format_version': '1.0',
                'name': 'TestPackage',
                'description': [
                    'This is a summary.',
                    '',
                    'This is a description.',
                ],
                'created_timestamp': '2015-10-10T08:17:29.958569',
                'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                'current_version': '1.0.0',
                'package_names': [
                    {
                        'system': ['centos', 'rhel'],
                        'name': 'reviewboard',
                        'type': 'rpm',
                    },
                ],
                'channel_aliases': {
                    'stable': '1.0.x',
                    'beta': '2.0.x',
                },
                'channels': [
                    {
                        'name': '1.0.x',
                        'created_timestamp': '2015-10-11T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-12T08:17:29.958569',
                        'latest_version': '1.0.0',
                        'current': True,
                        'visible': True,
                        'manifest_file': '1.0.x.json',
                    },
                ]
            })

    def test_current_channel(self):
        """Testing PackageBundle.current_channel"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')
        bundle._loaded = True

        channel1 = PackageChannel(
            bundle=bundle,
            name='beta',
            current=False,
            visible=True,
            manifest_url='beta.json')
        channel2 = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            current=True,
            visible=True,
            manifest_url='1.0.x.json')
        channel3 = PackageChannel(
            bundle=bundle,
            name='0.5.x',
            current=False,
            visible=True,
            manifest_url='0.5.x.json')
        bundle._channels = [channel1, channel2, channel3]

        self.assertEqual(bundle.current_channel, channel2)

    def test_current_channel_with_no_current(self):
        """Testing PackageBundle.current_channel with no current channel"""
        bundle = PackageBundle(manifest_url='packages/TestPackage/index.json')
        bundle._loaded = True

        channel = PackageChannel(
            bundle=bundle,
            name='staging',
            current=False,
            visible=False,
            manifest_url='staging.json')
        bundle._channels = [channel]

        self.assertEqual(bundle.current_channel, None)
