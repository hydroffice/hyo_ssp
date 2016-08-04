from __future__ import absolute_import, division, print_function, unicode_literals

import datetime as dt
import numpy as np
import logging

log = logging.getLogger(__name__)

from .base_format import BaseFormat, FormatError
from ..ssp_dicts import Dicts
from .. import __version__


class Leidos(BaseFormat):

    def __init__(self, file_content):
        super(Leidos, self).__init__(file_content=file_content)

        self.name = "LDS"
        self.driver = "%s.%s" % (self.name, __version__)

        log.info("reading ...")
        lines = self.file_content.splitlines()

        # identify format
        mid_line = lines[int(len(lines)/2)].strip()
        comma_tokens = mid_line.split(',')
        if len(comma_tokens) > 1:
            self._read_header_v14(lines)
            self._read_body_v14(lines)
        else: # it should be white-spaced
            self._read_header_svp(lines)
            self._read_body_svp(lines)

    def _read_header_v14(self, lines):
        log.info("reading > v14 header")

        token_header = "$MVS"
        header = lines[0]

        if header[:len(token_header)] != token_header:
            log.warning("unknown Leidos v14 format with header starting with: %s" % header[:len(token_header)])

        else:
            hdr_tokens = header.split(',')

            try:
                if len(hdr_tokens) == 9:
                    self.dg_time = dt.datetime(int(hdr_tokens[8]), int(hdr_tokens[7]), int(hdr_tokens[6]),
                                               int(hdr_tokens[3]), int(hdr_tokens[4]), int(hdr_tokens[5]))
                    log.info("date: %s" % self.dg_time)

            except ValueError:
                log.error("unable to parse date and time from: %s" % header)

        self.probe_type = Dicts.probe_types["Leidos"]
        log.info("probe type: %s" % self.probe_type)
        self.sensor_type = Dicts.sensor_types["SVP"]
        log.info("sensor type: %s" % self.sensor_type)

        self.num_samples = len(lines)
        log.info("max number of samples: %s" % self.num_samples)

        self.depth = np.zeros(self.num_samples)
        self.speed = np.zeros(self.num_samples)
        self.temperature = np.zeros(self.num_samples)
        self.salinity = np.zeros(self.num_samples)

    def _read_header_svp(self, lines):
        log.info("reading > svp header")

        token_header = "000"
        header = lines[0]

        if header[:len(token_header)] != token_header:
            log.warning("unknown Leidos svp format with header starting with: %s" % header[:len(token_header)])

        else:
            hdr_tokens = header.split(' ')

            try:
                if len(hdr_tokens) == 11:
                    # cast date-time
                    token_dt = hdr_tokens[5] + " " + hdr_tokens[4]
                    self.dg_time = dt.datetime.strptime(token_dt, '%y%j %H%M%S')
                    log.info("date: %s" % self.dg_time)

                    # latitude
                    latitude = float(hdr_tokens[2])
                    if latitude != 0.0:  # assumed empty fields?
                        self.latitude = latitude

                    # longitude
                    longitude = float(hdr_tokens[3])
                    if longitude != 0.0:  # assumed empty fields?
                        self.longitude = longitude

            except ValueError:
                log.error("unable to parse date and time from: %s" % header)

        self.probe_type = Dicts.probe_types["Leidos"]
        log.info("probe type: %s" % self.probe_type)
        self.sensor_type = Dicts.sensor_types["SVP"]
        log.info("sensor type: %s" % self.sensor_type)

        self.num_samples = len(lines)
        log.info("max number of samples: %s" % self.num_samples)

        self.depth = np.zeros(self.num_samples)
        self.speed = np.zeros(self.num_samples)
        self.temperature = np.zeros(self.num_samples)
        self.salinity = np.zeros(self.num_samples)

    def _read_body_v14(self, lines):
        log.info("reading > v14 body")

        samples = 0
        for i, line in enumerate(lines):

            # Skip over the header
            if i == 0:
                continue

            # remove leading 0s
            line = line.strip()

            # In case an incomplete file comes through
            try:
                dpt, spd = line.split(',')

                if spd == 0.0:
                    log.info("skipping 0-speed row at line %d: %s" % (i, line))
                    continue

                self.depth[samples] = float(dpt)
                self.speed[samples] = float(spd)
                log.info("%d %7.1f %7.1f" % (samples, self.depth[samples], self.speed[samples]))

            except ValueError:
                log.error("skipping line %s" % i)
                continue

            samples += 1

        log.info("good samples: %s" % samples)

        if self.num_samples != samples:
            log.info("resizing from %s to %s" % (self.num_samples, samples))
            self.depth.resize(samples)
            self.speed.resize(samples)
            self.temperature.resize(samples)
            self.salinity.resize(samples)
            self.num_samples = samples

    def _read_body_svp(self, lines):
        log.info("reading > svp body")

        samples = 0
        for i, line in enumerate(lines):

            # Skip over the header
            if i == 0:
                continue

            # remove leading 0s
            line = line.strip()

            # In case an incomplete file comes through
            try:
                dpt, spd = line.split()

                if spd == 0.0:
                    log.info("skipping 0-speed row at line %d: %s" % (i, line))
                    continue

                self.depth[samples] = float(dpt)
                self.speed[samples] = float(spd)
                log.info("%d %7.1f %7.1f" % (samples, self.depth[samples], self.speed[samples]))

            except ValueError:
                log.error("skipping line %s" % i)
                continue

            samples += 1

        log.info("good samples: %s" % samples)

        if self.num_samples != samples:
            log.info("resizing from %s to %s" % (self.num_samples, samples))
            self.depth.resize(samples)
            self.speed.resize(samples)
            self.temperature.resize(samples)
            self.salinity.resize(samples)
            self.num_samples = samples