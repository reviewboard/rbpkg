from __future__ import unicode_literals

import re
import unittest


class TestCase(unittest.TestCase):
    """Base class for test cases."""

    ws_re = re.compile(r'\s+')

    def shortDescription(self):
        """Return the description of the current test.

        This changes the default behavior to replace all newlines with spaces,
        allowing a test description to span lines. It should still be kept
        short, though.

        Returns:
            unicode:
            The short description of the current test.
        """
        doc = self._testMethodDoc

        if doc is not None:
            doc = doc.split('\n\n', 1)[0]
            doc = self.ws_re.sub(' ', doc).strip()

        return doc
