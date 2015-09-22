from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import numpy as np

from .base_format import BaseFormat, FormatError
from .. import __version__
from ..ssp_dicts import Dicts


class Saiv(BaseFormat):

    def __init__(self, file_content, verbose=True, callback_print_func=None):
        super(Saiv, self).__init__(file_content=file_content, verbose=verbose,
                                   callback_print_func=callback_print_func)
        self.name = "SAI"
        self.driver = self.name + (".%s" % __version__)

        self.header_token = 'Ser\tMeas'
        self.depth_token = 'Press'
        self.speed_token = 'S. vel.'
        self.temp_token = 'Temp'
        self.sal_token = 'Sal.'
        self.date_token = 'Date'
        self.time_token = 'Time'
        self.probe_type_token = 'From file:'

        self.print_info("reading ...")
        lines = self.file_content.splitlines()

        self._read_header(lines)
        self._read_body(lines)

    def _read_header(self, lines):
        self.print_info("reading > header")

        got_date = False
        got_time = False
        got_depth = False
        got_speed = False
        got_temperature = False
        got_salinity = False
        got_cast_header = False

        probe_type = ''

        self.samples_offset = 0

        for line in lines:

            if line[:len(self.header_token)] == self.header_token:
                got_cast_header = True
                self.print_info("header line for fields: %s" % line)

                column = 0
                for field_type in line.split('\t'):
                    self.data_index[field_type] = int(column)
                    if field_type == self.depth_token:
                        self.print_info('col for pressure: %s' % column)
                        got_depth = True
                    elif field_type == self.temp_token:
                        self.print_info('col for temperature: %s' % column)
                        got_temperature = True
                    elif field_type == self.sal_token:
                        self.print_info('col for salinity: %s' % column)
                        got_salinity = True
                    elif field_type == self.speed_token:
                        self.print_info('col for sound speed: %s' % column)
                        got_speed = True
                    elif field_type == self.date_token:
                        self.print_info('col for date: %s' % column)
                        got_date = True
                    elif field_type == self.time_token:
                        self.print_info('col for time: %s' % column)
                        got_time = True
                    column += 1

                self.samples_offset += 2
                break

            elif line[:len(self.probe_type_token)] == self.probe_type_token:
                try:
                    probe_type = line.split(':')[1].split()[0].strip()
                    self.print_info('probe type: %s' % probe_type)
                except (IndexError, ValueError):
                    pass

            self.samples_offset += 1

        if not got_cast_header or \
                not got_depth or not got_speed or not got_temperature or not got_salinity or \
                not got_date or not got_time:
            if not got_cast_header:
                self.print_error("missing cast header")
            if not got_depth:
                self.print_error("missing depth field (need depth 'Depth' field)")
            if not got_speed:
                self.print_error("missing speed field (need speed 'Sound Velocity (calc)' field)")
            if not got_temperature:
                self.print_error("missing temperature field (need temperature 'Temperature' field)")
            if not got_salinity:
                self.print_error("missing salinity field (need salinity 'Salinity' field)")
            if not got_date:
                self.print_error("missing date field (need date 'Date' field)")
            if not got_time:
                self.print_error("missing time field (need time 'Time' field)")
            return

        self.num_samples = len(lines) - self.samples_offset
        if self.num_samples == 0:
            self.print_error('no data samples')
            return
        self.print_info('samples: %s' % self.num_samples)

        if probe_type != 'S2':
            self.print_info("unknown probe type: %s -> forcing S2" % probe_type)
            probe_type = 'S2'
        self.probe_type = Dicts.probe_types[probe_type]

        self.sensor_type = Dicts.sensor_types["CTD"]
        self.depth = np.zeros(self.num_samples)
        self.speed = np.zeros(self.num_samples)
        self.temperature = np.zeros(self.num_samples)
        self.salinity = np.zeros(self.num_samples)

    def _read_body(self, lines):
        self.print_info("reading > body")

        count = 0
        valid_date = False
        valid_time = False
        for line in lines[self.samples_offset:len(lines)]:
            try:
                # In case an incomplete file comes through
                data = line.split()
                self.depth[count] = float(data[self.data_index[self.depth_token]])
                self.speed[count] = float(data[self.data_index[self.speed_token]])
                self.temperature[count] = float(data[self.data_index[self.temp_token]])
                self.salinity[count] = float(data[self.data_index[self.sal_token]])

                if not valid_date and not valid_time:
                    # date
                    date_string = data[self.data_index[self.date_token]]
                    month = int(date_string.split('/')[1])
                    day = int(date_string.split('/')[0])
                    year = int(date_string.split('/')[2])
                    valid_date = True
                    self.print_info('date: %s/%s/%s' % (day, month, year))
                    # time
                    time_string = data[self.data_index[self.time_token]]
                    valid_time = True
                    hour = int(time_string.split(':')[0])
                    minute = int(time_string.split(':')[1])
                    second = int(time_string.split(':')[2])
                    self.print_info('time: %s:%s:%s' % (hour, minute, second))

                    if (year is not None) and (hour is not None):
                        self.dg_time = dt.datetime(year, month, day, hour, minute, second)

            except ValueError:
                self.print_error("skipping line %s" % count)
                continue
            count += 1

        if self.num_samples != count:
            self.depth.resize(count)
            self.speed.resize(count)
            self.temperature.resize(count)
            self.salinity.resize(count)
            self.num_samples = count