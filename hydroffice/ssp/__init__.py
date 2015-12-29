"""
Hydro-Package
SSP
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

__version__ = '2.1.0'
__doc__ = "SSP"
__author__ = 'gmasetti@ccom.unh.edu; brc@ccom.unh.edu'
__license__ = 'BSD license'
__copyright__ = 'Copyright 2015 University of New Hampshire, Center for Coastal and Ocean Mapping'


# def hyo():
# def hyo_app():
def hyo_lib():
    return __doc__, __version__
