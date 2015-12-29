from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
from hydroffice.ssp.project import Project


class TestProject(unittest.TestCase):

    import os
    prj = Project(with_listeners=False, with_woa09=False, with_rtofs=False)
    prj.release()

    def test_setting_getting_output_folder(self):
        import os
        test_dir = os.path.curdir
        self.prj.set_output_folder(test_dir)
        self.assertTrue(self.prj.get_output_folder() == test_dir)

