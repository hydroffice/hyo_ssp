from __future__ import absolute_import, division, print_function, unicode_literals

import os

from ..base.log_db import LogDb
from .helper import Helper


class SspLogDb(LogDb):
    """class that stores logs in a SQLite db"""

    def __init__(self, db_path=None, max_entries=10000, verbose=False, callback_print_func=None):
        if not db_path:
            db_path = os.path.join(Helper.default_projects_folder(), "__log__.db")
        super(SspLogDb, self).__init__(db_path=db_path, max_entries=max_entries,
                                       verbose=verbose, callback_print_func=callback_print_func)