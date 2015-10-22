from __future__ import unicode_literals

import platform

from kgb import SpyAgency

from rbpkg.testing.testcases import TestCase
from rbpkg.utils.matches import matches_current_system, matches_version_range


class MatchesTests(SpyAgency, TestCase):
    """Unit tests for rbpkg.utils.matches."""

    def setUp(self):
        super(MatchesTests, self).setUp()

        self.simulate_system = 'Linux'

        self.spy_on(platform.system, call_fake=lambda: self.simulate_system)
        self.spy_on(platform.dist, call_fake=lambda: ('MyDistro', '1.3', ''))

    def test_matches_current_system_with_wildcard(self):
        """Testing matches_current_system with wildcard for system"""
        self.assertTrue(matches_current_system(['*']))

    def test_matches_current_system_with_name_only(self):
        """Testing matches_current_system with matching and name only"""
        self.assertTrue(matches_current_system(['Foo', 'MyDistro']))
        self.assertFalse(matches_current_system(['Foo']))

    def test_matches_current_system_with_version_equality(self):
        """Testing matches_current_system with matching and version equality"""
        self.assertTrue(matches_current_system(['MyDistro==1.3']))
        self.assertFalse(matches_current_system(['MyDistro==1.4']))

    def test_matches_current_system_with_version_range(self):
        """Testing matches_current_system with matching and version range"""
        self.assertTrue(matches_current_system(['MyDistro>1.2,<1.4']))
        self.assertFalse(matches_current_system(['MyDistro>1.3,<1.4']))

    def test_matches_current_system_mac(self):
        """Testing matches_current_system on MacOS X"""
        self.simulate_system = 'Darwin'
        self.spy_on(platform.mac_ver,
                    call_fake=lambda: ('10.10.4', ('', '', ''), 'x86_64'))

        self.assertTrue(matches_current_system(['macosx']))
        self.assertTrue(matches_current_system(['macosx>=10.10']))
        self.assertFalse(matches_current_system(['macosx>=10.10.5']))
        self.assertTrue(matches_current_system(['*']))

    def test_matches_current_system_windows(self):
        """Testing matches_current_system on Windows"""
        self.simulate_system = 'Windows'
        self.spy_on(platform.win32_ver,
                    call_fake=lambda: ('XP', '5.1.2600', 'SP2',
                                       'Multiprocessor Free'))

        self.assertTrue(matches_current_system(['windows']))
        self.assertTrue(matches_current_system(['windows>=5.1']))
        self.assertFalse(matches_current_system(['windows>=5.2']))
        self.assertTrue(matches_current_system(['*']))

    def test_matches_version_range_with_name_only(self):
        """Testing matches_version_range with name only"""
        self.assertTrue(matches_version_range('1.0', 'foo', 'foo'))
        self.assertFalse(matches_version_range('1.0', 'foo', 'bar'))

    def test_matches_version_range_with_equality(self):
        """Testing matches_version_range with equality only"""
        self.assertTrue(matches_version_range('1.0', 'foo==1.0'))
        self.assertFalse(matches_version_range('2.0', 'foo==1.0'))

    def test_matches_version_range_with_range(self):
        """Testing matches_version_range with version range"""
        self.assertTrue(matches_version_range('2.0', 'foo>=1.0,<3.0'))
        self.assertFalse(matches_version_range('2.0', 'foo>2.0,<3.0'))
