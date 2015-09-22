from __future__ import absolute_import, division, print_function, unicode_literals

from ..udpio import UdpIO
from . import mvp
from ...helper import SspError


class MvpCastIO(UdpIO):
    def __init__(self, listen_port, desired_datagrams, timeout, protocol, fmt,
                 verbose=True, callback_print_func=None):
        UdpIO.__init__(self, listen_port, desired_datagrams, timeout, verbose, callback_print_func)
        self.name = "MVP"
        self.cast = None

        try:
            self.protocol = mvp.Mvp.protocols[protocol]
        except KeyError:
            raise SspError("passed unknown protocol: %s" % protocol)
        try:
            self.format = mvp.Mvp.formats[fmt]
        except KeyError:
            raise SspError("passed unknown format: %s" % fmt)

        self.header = str()
        self.footer = str()
        self.data_blocks = []

        self.num_data_blocks = 0

        self.got_header = False
        self.got_data = False
        self.got_footer = False

    def parse(self):
        self.print_info("Going to parse data of length %s using protocol %s" % (len(self.data), self.protocol))

        if self.protocol == mvp.Mvp.protocols["NAVO_ISS60"]:

            if len(self.data) == 536:
                self.print_info("got header")
                self.header = self.data
                self.got_header = True
                self.got_footer = False
                self.got_data = False
                self.num_data_blocks = 0

            elif len(self.data) == 20032:
                self.print_info(" got data block")
                self.got_data = True
                self.data_blocks.append(self.data)
                self.num_data_blocks += 1

            elif len(self.data) == 8:
                self.print_info("got footer")
                self.footer = self.data
                self.got_footer = True

            if self.got_header and self.got_data and self.got_footer:
                self.print_info("going to assemble cast!")
                self.print_info("got lengths: %s %s %s"
                                % (len(self.header), len(self.data_blocks), len(self.footer)))
                self.print_info("got num data blocks: %s" % self.num_data_blocks)

                self.cast = mvp.Mvp(self.header, self.data_blocks, self.footer, self.protocol, self.format)

                self.got_header = False
                self.header = None
                self.got_data = False
                self.data_blocks = []
                self.num_data_blocks = 0
                self.got_footer = False
                self.footer = None

        elif self.protocol == mvp.Mvp.protocols["UNDEFINED"]:
            self.print_info("going to parse with UNDEFINED protocol!!")
            self.print_info("the data is %s" % self.data)
            self.data_blocks.append(self.data)
            self.num_data_blocks += 1
            self.cast = mvp.Mvp(self.header, self.data_blocks, self.footer, self.protocol, self.format)
