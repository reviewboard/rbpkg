from __future__ import unicode_literals

from datetime import datetime

from rbpkg.api.package_bundle import PackageBundle
from rbpkg.api.package_channel import PackageChannel
from rbpkg.api.tests.testcases import PackagesTestCase


class PackageBundleTests(PackagesTestCase):
    """Unit tests for rbpkg.api.package.PackageBundle."""

    def test_deserialize_with_all_info(self):
        """Testing PackageBundle.deserialize with all available info"""
        bundle = PackageBundle.deserialize(
            'packages/TestPackage/index.json',
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
                         'packages/TestPackage/index.json')
        self.assertEqual(bundle.name, 'TestPackage')
        self.assertEqual(bundle.description,
                         'This is the summary.\n'
                         '\n'
                         'This is the multi-line\n'
                         'description.')
        self.assertEqual(bundle.created_timestamp,
                         datetime(2015, 10, 10, 8, 17, 29, 958569))
        self.assertEqual(bundle.last_updated_timestamp,
                         datetime(2015, 10, 15, 8, 17, 29, 958569))
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
            'packages/TestPackage/index.json',
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
                         'packages/TestPackage/index.json')
        self.assertEqual(bundle.name, 'TestPackage')
        self.assertEqual(bundle.description, None)
        self.assertEqual(bundle.created_timestamp,
                         datetime(2015, 10, 10, 8, 17, 29, 958569))
        self.assertEqual(bundle.last_updated_timestamp,
                         datetime(2015, 10, 15, 8, 17, 29, 958569))
        self.assertEqual(bundle.channel_aliases, {})

        # The exact details will be compared in a later unit test. Just
        # sanity-check that we have what we expect.
        self.assertEqual(len(bundle.channels), 2)
        self.assertEqual(bundle.channels[0].name, '2.0.x')
        self.assertEqual(bundle.channels[1].name, '1.0.x')

    def test_serialize(self):
        """Testing PackageBundle.serialize"""
        bundle = PackageBundle(
            name='TestPackage',
            description='This is a summary.\n\nThis is a description.',
            created_timestamp=datetime(2015, 10, 10, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 15, 8, 17, 29, 958569),
            channel_aliases={
                'stable': '1.0.x',
                'beta': '2.0.x',
            })

        channel = PackageChannel(
            bundle=bundle,
            name='1.0.x',
            created_timestamp=datetime(2015, 10, 11, 8, 17, 29, 958569),
            last_updated_timestamp=datetime(2015, 10, 12, 8, 17, 29, 958569),
            latest_version='1.0.0',
            current=True,
            visible=True,
            manifest_url='1.0.x.json')
        bundle.channels = [channel]

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
