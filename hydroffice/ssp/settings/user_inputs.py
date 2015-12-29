from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import logging

log = logging.getLogger(__name__)

from hydroffice.ssp.ssp_dicts import Dicts
from hydroffice.ssp.helper import SspError


class UserInputs(object):

    def __init__(self):

        self.filename_prefix = None
        self.server_caris_filename = ""
        self.inspection_mode = Dicts.inspections_mode['Zoom']

        # user insert
        self.user_speed = None
        self.user_salinity = None
        self.user_temperature = None
        self.user_depth = None

        # metadata
        self.log_processing_metadata = False
        self.log_server_metadata = False

        # export
        self.user_filename_prefix = None
        self.user_export_directory = None
        self.export_formats = {
            'ASVP': False,
            'PRO': False,
            'VEL': False,
            'HIPS': False,
            'IXBLUE': False,
            'UNB': False,
            'ELAC': False,
            'CSV': False
        }

    def clear_user_samples(self):
        self.user_speed = None
        self.user_salinity = None
        self.user_temperature = None
        self.user_depth = None

    def switch_export_format(self, fmt):
        log.debug("switching %s" % fmt)

        try:
            self.export_formats[fmt] = not self.export_formats[fmt]

        except KeyError:
            raise SspError("Unknown export data format: %s" % fmt)

    def __str__(self):
        output = " # User Inputs (time stamp: %s) #\n\n" % datetime.datetime.now().isoformat()

        output += "\n > Filename prefix: %s\n" % self.filename_prefix
        output += "\n > Inspection mode: %s >> %s\n" \
                  % (self.inspection_mode, Dicts.first_match(Dicts.inspections_mode, self.inspection_mode))
        output += "\n > Server: server_caris_filename: %s\n" % self.server_caris_filename

        output += "\n > User insert\n"
        output += "   - user_speed:  %s\n" % self.user_speed
        output += "   - user_salinity:  %s\n" % self.user_salinity
        output += "   - user_temperature:  %s\n" % self.user_temperature
        output += "   - user_depth:  %s\n" % self.user_depth

        output += "\n > Metadata\n"
        output += "   - log_server_metadata: %s\n" % self.log_server_metadata
        output += "   - log_processing_metadata: %s\n" % self.log_processing_metadata

        output += "\n > Export:\n"
        output += "   - user_filename_prefix:  %s\n" % self.user_filename_prefix
        output += "   - user_export_directory:  %s\n" % self.user_export_directory


        output += "\n > Export formats:\n"
        for fmt in self.export_formats:
            output += "   - %s: %s\n" % (fmt, self.export_formats[fmt])

        return output
