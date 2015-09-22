import datetime as dt

import netCDF4
import numpy as np

from .base_format import BaseFormat
from .. import __version__
from ..ssp_dicts import Dicts


class Turo(BaseFormat):
    def __init__(self, filename, verbose=True, callback_print_func=None):
        self.original_path = filename
        super(Turo, self).__init__(file_content=netCDF4.Dataset(self.original_path), verbose=verbose,
                                   callback_print_func=callback_print_func)
        self.name = "TUR"
        self.driver = self.name + (".%s" % __version__)

        self.print_info("reading ...")

        self._read_header(None)
        self._read_body(None)

    def _read_header(self, lines):
        self.print_info("reading > header")

        woce_date = str(self.file_content.variables['woce_date'][0])
        # The hours in the time field don't have a leading zero so forcing to print
        # as a 6 digit integer with leading zeros
        woce_time = "%.6d" % self.file_content.variables['woce_time'][0]

        self.dg_time = dt.datetime(int(woce_date[0:4]), int(woce_date[4:6]), int(woce_date[6:8]), int(woce_time[0:2]),
                                   int(woce_time[2:4]), int(woce_time[4:6]), 0)
        self.print_info("time: %s" % self.dg_time)

        self.latitude = self.file_content.variables['latitude'][0]
        self.print_info("latitude: %s" % self.latitude)

        self.longitude = self.file_content.variables['longitude'][0]
        self.print_info("longitude: %s" % self.longitude)

        self.probe_type = Dicts.probe_types["XBT"]
        self.print_info("probe type: %s" % self.probe_type)

        self.sensor_type = Dicts.sensor_types["XBT"]
        self.print_info("sensor type: %s" % self.sensor_type)

    def _read_body(self, lines):
        self.print_info("reading > body")

        self.depth = self.file_content.variables['depth'][:]
        self.speed = self.file_content.variables['soundSpeed'][0, :, 0, 0]
        self.temperature = self.file_content.variables['temperature'][0, :, 0, 0]
        self.num_samples = self.depth.size
        self.salinity = np.zeros(self.num_samples)
        self.print_info("total samples: %s" % self.num_samples)

        self.file_content.close()
