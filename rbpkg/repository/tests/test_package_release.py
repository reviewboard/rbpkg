from __future__ import unicode_literals

from rbpkg.repository.package_bundle import PackageBundle
from rbpkg.repository.package_channel import PackageChannel
from rbpkg.repository.package_release import PackageRelease
from rbpkg.repository.tests.testcases import PackagesTestCase


class PackageReleaseTests(PackagesTestCase):
    """Unit tests for rbpkg.repository.package.PackageRelease."""

    def test_deserialize_with_all_info(self):
        """Testing PackageRelease.deserialize with all available info"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)
        release = PackageRelease.deserialize(
            channel,
            {
                'version': '1.0',
                'type': 'beta',
                'visible': False,
                'release_notes_url': 'https://example.com/1.0/',
            })

        self.assertEqual(release.version, '1.0')
        self.assertEqual(release.release_type, PackageRelease.TYPE_BETA)
        self.assertFalse(release.visible)
        self.assertEqual(release.release_notes_url, 'https://example.com/1.0/')

    def test_deserialize_with_minimum_info(self):
        """Testing PackageRelease.deserialize with minimum info"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)
        release = PackageRelease.deserialize(
            channel,
            {
                'version': '1.0',
            })

        self.assertEqual(release.version, '1.0')
        self.assertEqual(release.release_type, PackageRelease.TYPE_STABLE)
        self.assertTrue(release.visible)
        self.assertEqual(release.release_notes_url, None)

    def test_serialize(self):
        """Testing PackageRelease.serialize"""
        bundle = PackageBundle()
        channel = PackageChannel(bundle)

        release = PackageRelease(
            channel=channel,
            version='1.0',
            release_type=PackageRelease.TYPE_BETA,
            visible=False,
            release_notes_url='https://example.com/1.0/')

        self.assertEqual(
            release.serialize(),
            {
                'version': '1.0',
                'type': 'beta',
                'visible': False,
                'release_notes_url': 'https://example.com/1.0/',
            })
