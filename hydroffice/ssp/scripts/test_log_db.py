from __future__ import absolute_import, division, print_function, unicode_literals

import os

from ...base.log_db import LogEntry
from ..log_db import SspLogDb
from ..ssp_dicts import Dicts


if __name__ == "__main__":

    #here = os.path.abspath(os.path.dirname(__file__))
    #test_db = SspLogDb(db_path=os.path.join(here, "tmp", "log.db"), max_entries=10)
    test_db = SspLogDb(max_entries=10)

    count = 0
    for i in range(12):
        new_entry = LogEntry("testing entry %s" % i)
        ret0 = test_db.add_entry(new_entry)
        if ret0:
            count += 1
    print("added entries: %s" % count)

    ret0 = test_db.list_all_entries()
    print(len(ret0))

    ret0 = test_db.list_all_entries_with_type(Dicts.log_types['info'])
    print(len(ret0))

    if len(ret0) > 0:
        entry = test_db.get_entry_by_id(ret0[0][0])
        print(entry)

    ret = test_db.delete_entries(num_entries=2)
    print("\ndelete 2 entries: %s" % ret)

    print("\ntotal logs rows: %s" % test_db.check_table_total_rows('logs', True))
    test_db.check_table_cols_settings('logs', True)
    test_db.check_tables_values_in_cols('logs', True)

    # close db
    print("\nclose db")
    test_db.close()
