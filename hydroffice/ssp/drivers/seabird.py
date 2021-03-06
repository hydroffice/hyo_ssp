from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
from time import strptime
import numpy as np
import logging

log = logging.getLogger(__name__)

from .base_format import BaseFormat, FormatError
from .. import __version__
from ..ssp_dicts import Dicts


class Seabird(BaseFormat):

    def __init__(self, file_content):
        super(Seabird, self).__init__(file_content=file_content)
        self.name = "SEB"
        self.driver = self.name + (".%s" % __version__)

        self.start_data_token = '*END*'
        self.time_token = '* System UpLoad Time'
        self.time_2_token = '* NMEA UTC (Time)'
        self.filename_token = '* FileName'
        self.latitude_token = '* NMEA Latitude ='
        self.longitude_token = '* NMEA Longitude ='
        self.latitude_2_token = '** Lat:'
        self.longitude_2_token = '** Lon:'
        self.field_name_token = '# name'
        self.depth_token = 'depSM'
        self.speed_token = ''
        self.temp_token = ''
        self.sal_token = ''

        log.info("reading ...")
        lines = self.file_content.splitlines()

        self._read_header(lines)
        self._read_body(lines)

    def _read_header(self, lines):
        log.info("reading > header")

        got_depth = False
        got_speed = False
        got_temperature = False
        got_salinity = False

        utc_time = None
        system_time = None
        latitude = None
        longitude = None
        filename = None

        for line in lines:
            if line[:len(self.start_data_token)] == self.start_data_token:
                self.samples_offset += 1
                break

            elif line[:len(self.time_token)] == self.time_token:
                try:
                    year = int(line.split()[-2])
                    day = int(line.split()[-3])
                    month_name = line.split()[-4]
                    month = strptime(month_name, '%b').tm_mon
                    time_string = line.split()[-1]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    system_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    log.error("failure in reading time token: %s" % line)

            elif line[:len(self.time_2_token)] == self.time_2_token:
                try:
                    year = int(line.split()[-2])
                    day = int(line.split()[-3])
                    month_name = line.split()[-4]
                    month = strptime(month_name, '%b').tm_mon
                    time_string = line.split()[-1]
                    hour, minute, second = [int(i) for i in time_string.split(':')]
                    utc_time = dt.datetime(year, month, day, hour, minute, second)
                except ValueError:
                    log.error("failure in reading time token: %s" % line)

            elif line[:len(self.filename_token)] == self.filename_token:
                filename = line.split("=")[-1]

            elif line[:len(self.latitude_token)] == self.latitude_token:
                try:
                    deg = float(line.split()[-3])
                    min_deg = float(line.split()[-2])
                    hemisphere = line.split()[-1]
                    latitude = deg + min_deg / 60.0
                    if hemisphere == "S":
                        latitude *= -1
                except ValueError:
                    log.error("failure in reading latitude token: %s" % line)

            elif line[:len(self.longitude_token)] == self.longitude_token:
                try:
                    deg = float(line.split()[-3])
                    min_deg = float(line.split()[-2])
                    hemisphere = line.split()[-1]
                    longitude = deg + min_deg / 60.0
                    if hemisphere == "W":
                        longitude *= -1
                except ValueError:
                    log.error("failure in reading longitude token: %s" % line)

            elif line[:len(self.latitude_2_token)] == self.latitude_2_token:
                try:
                    values = line.split()[-2]
                    deg = float(values.split(';')[-3])
                    min_deg = float(values.split(';')[-2])
                    sec_deg = float(values.split(';')[-1])
                    hemisphere = line.split()[-1]
                    latitude = deg + min_deg / 60.0 + sec_deg / 3600.0
                    if hemisphere == "S":
                        latitude *= -1
                    # log.debug("lat: %s from %s" % (latitude, line))
                except ValueError as e:
                    log.error("failure in reading latitude token: %s\n%s" % (line, e))

            elif line[:len(self.longitude_2_token)] == self.longitude_2_token:
                try:
                    values = line.split()[-2]
                    deg = float(values.split(';')[-3])
                    min_deg = float(values.split(';')[-2])
                    sec_deg = float(values.split(';')[-1])
                    hemisphere = line.split()[-1]
                    longitude = deg + min_deg / 60.0 + sec_deg / 3600.0
                    if hemisphere == "W":
                        longitude *= -1
                    # log.debug("long: %s from %s" % (longitude, line))
                except ValueError:
                    log.error("failure in reading longitude token: %s\n%s" % (line, e))

            elif line[:len(self.field_name_token)] == self.field_name_token:
                column = line.split()[2]
                field_type = line.split()[4].split(":")[0]
                self.data_index[field_type] = int(column)
                if field_type == 'depSM':
                    got_depth = True
                    self.depth_is_pressure = False
                    self.depth_token = field_type
                elif field_type == 'prdM':
                    if not got_depth:  # we prefer depSM if available
                        got_depth = True
                        self.depth_is_pressure = True
                        self.depth_token = field_type
                elif (field_type == 'svCM') or (field_type == 'svDM'):
                    got_speed = True
                    self.speed_token = field_type
                elif field_type == "t090C" or field_type == "tv290C":
                    got_temperature = True
                    self.temp_token = field_type
                elif field_type == 'sal00':
                    self.salinity_is_conductivity = False
                    got_salinity = True
                    self.sal_token = field_type
                elif field_type == 'c0S/m':
                    if not got_salinity:  # we prefer sal00 if available
                        self.salinity_is_conductivity = True
                        got_salinity = True
                        self.sal_token = field_type

            self.samples_offset += 1

        if not got_depth or not got_temperature or not got_salinity:
            if not got_depth:
                log.error("Missing depth field (need depth 'depSM' field)")
            if not got_temperature:
                log.error("Missing temperature field (need temperature 't090C' or 'tv290C' field)")
            if not got_salinity:
                log.error("Missing salinity field (need salinity 'sal00' field)")
            return

        if not got_speed:
            self.missing_sound_speed = True

        self.original_path = filename
        self.latitude = latitude
        self.longitude = longitude

        # print "Got latitude, longitude", latitude, longitude

        if utc_time:
            # We prefer UTC time over system time
            self.dg_time = utc_time
        elif system_time:
            self.dg_time = system_time
        else:
            self.dg_time = None

        self.sensor_type = Dicts.sensor_types['CTD']
        self.probe_type = Dicts.probe_types['SBE']

        self.num_samples = len(lines) - self.samples_offset
        log.debug("number of samples: %s" % self.num_samples)

        self.depth = np.zeros(self.num_samples)
        self.speed = np.zeros(self.num_samples)
        self.temperature = np.zeros(self.num_samples)
        self.salinity = np.zeros(self.num_samples)

    def _read_body(self, lines):
        log.info("reading > body")
        # log.debug("data index: %s" % self.data_index)

        count = 0
        for line in lines[self.samples_offset:len(lines)]:
            try:
                # In case an incomplete file comes through
                data = line.split()

                # data retrieval
                depth_value = float(data[self.data_index[self.depth_token]])
                temp_value = float(data[self.data_index[self.temp_token]])
                if not self.missing_sound_speed:
                    speed_value = float(data[self.data_index[self.speed_token]])
                if self.salinity_is_conductivity:
                    sal_value = float(data[self.data_index[self.sal_token]]) * 10  # from S/m to mmho/cm
                else:
                    sal_value = float(data[self.data_index[self.sal_token]])

                # filter to skip anomalous data
                if not self.missing_sound_speed:
                    if (speed_value < 1000) or (speed_value > 2000):
                        log.error("skipping for anomalous speed value: %s" % speed_value)
                        continue
                if (temp_value < -10) or (temp_value > 100):
                    log.error("skipping for anomalous temp value: %s" % temp_value)
                    continue
                if self.salinity_is_conductivity:
                    if sal_value < 0:
                        log.error("skipping for anomalous conductivity value: %s" % sal_value)
                        continue
                else:
                    if sal_value < 0:
                        log.error("skipping for anomalous sal value: %s" % sal_value)
                        continue

                # data storing
                self.depth[count] = depth_value
                if not self.missing_sound_speed:
                    self.speed[count] = speed_value
                self.temperature[count] = temp_value
                self.salinity[count] = sal_value

            except ValueError:
                log.error("failure at sample %s" % count)
                continue

            count += 1

        log.info("parsed %s samples" % count)

        if self.num_samples != count:
            self.depth.resize(count)
            self.speed.resize(count)
            self.temperature.resize(count)
            self.salinity.resize(count)
            self.num_samples = count
