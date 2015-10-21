from __future__ import unicode_literals

from datetime import datetime

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_index import PackageIndex
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageIndexTests(PackagesTestCase):
    """Unit tests for rbpkg.repository.package.PackageIndex."""

    def test_deserialize(self):
        """Testing PackageIndex.deserialize"""
        index = PackageIndex.deserialize(
            'packages/index.json',
            {
                'format_version': '1.0',
                'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                'bundles': [
                    {
                        'name': 'ReviewBoard',
                        'manifest_file': 'packages/ReviewBoard/index.json',
                        'created_timestamp': '2015-10-10T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                        'current_version': '2.0.20',
                        'package_names': [
                            {
                                'system': ['centos', 'rhel'],
                                'name': 'reviewboard',
                                'type': 'rpm',
                            },
                        ],
                    },
                ],
            })

        self.assertEqual(index.manifest_url, 'packages/index.json')
        self.assertEqual(index.last_updated_timestamp,
                         datetime(2015, 10, 15, 8, 17, 29, 958569))
        self.assertEqual(len(index.bundles), 1)

        bundle = index.bundles[0]
        self.assertTrue(isinstance(bundle, PackageBundle))
        self.assertEqual(bundle.name, 'ReviewBoard')
        self.assertEqual(bundle.manifest_url,
                         'packages/ReviewBoard/index.json')
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
        self.assertFalse(bundle._loaded)

    def test_serialize(self):
        """Testing PackageIndex.serialize"""
        index = PackageIndex(
            manifest_url='packages/index.json',
            last_updated_timestamp=datetime(2015, 10, 15, 8, 17, 29, 958569))

        index.bundles = [
            PackageBundle(
                name='TestPackage',
                manifest_url='packages/TestPackage/index.json',
                created_timestamp=datetime(2015, 10, 10, 8, 17, 29, 958569),
                last_updated_timestamp=datetime(2015, 10, 15, 8, 17, 29,
                                                958569),
                current_version='1.0.5',
                package_names=[
                    {
                        'system': ['centos', 'rhel'],
                        'name': 'testpackage',
                        'type': 'rpm',
                    },
                ]),
        ]

        self.assertEqual(
            index.serialize(),
            {
                'format_version': '1.0',
                'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                'bundles': [
                    {
                        'name': 'TestPackage',
                        'manifest_file': 'packages/TestPackage/index.json',
                        'created_timestamp': '2015-10-10T08:17:29.958569',
                        'last_updated_timestamp': '2015-10-15T08:17:29.958569',
                        'current_version': '1.0.5',
                        'package_names': [
                            {
                                'system': ['centos', 'rhel'],
                                'name': 'testpackage',
                                'type': 'rpm',
                            },
                        ],
                    },
                ],
            })
