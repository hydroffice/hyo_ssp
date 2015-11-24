from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from hydroffice.ssp.helper import SspError, Helper


class TestSSPError(unittest.TestCase):

    err = SspError("test")

    def test_is_instance(self):
        self.assertTrue(isinstance(self.err, Exception))

    def test_raise(self):
        with self.assertRaises(SspError):
            raise self.err

    def test_has_message(self):
        self.assertTrue(hasattr(self.err, 'message'))


class TestHelper(unittest.TestCase):

    hlp = Helper()

    def test_default_projects_folder(self):
        import os
        self.assertTrue(os.path.exists(self.hlp.default_projects_folder()))

    def test_pkg_info(self):
        output = self.hlp.pkg_info()
        self.assertTrue("gmasetti@ccom.unh.edu" in str(output))

    # ### END OF SHARED WITH BASE.HELPER ###
