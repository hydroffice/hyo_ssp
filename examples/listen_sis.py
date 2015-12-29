from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import time

from hydroffice.ssp.io.kmio import KmIO

log = logging.getLogger(__name__)

# logging settings
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
logger.addHandler(ch)

km_listener = KmIO(3500, [0x50, 0x52, 0x55, 0x58], 1)
km_listener.start_listen()
time.sleep(2)
km_listener.request_iur("192.168.1.22")
time.sleep(3)
km_listener.stop_listen()
print(km_listener.nav)
print(km_listener.ssp)
print(km_listener.bist)
print(km_listener.installation)
print(km_listener.range_angle78)



