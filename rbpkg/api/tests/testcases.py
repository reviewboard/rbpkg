from __future__ import unicode_literals

from unittest import TestCase

from rbpkg.api.loaders import InMemoryPackageDataLoader, set_data_loader


class PackagesTestCase(TestCase):
    """Base class for the packages tests.

    This takes care of setting up an in-memory data loader, so that responses
    can be populated without hitting the main repository.
    """

    def setUp(self):
        self.data_loader = InMemoryPackageDataLoader()
        set_data_loader(self.data_loader)

    def tearDown(self):
        set_data_loader(None)
