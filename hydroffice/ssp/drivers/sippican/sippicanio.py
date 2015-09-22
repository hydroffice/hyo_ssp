from __future__ import absolute_import, division, print_function, unicode_literals

from ..udpio import UdpIO
from . import sippican


class SippicanIO(UdpIO):

    def __init__(self, listen_port, desired_datagrams, timeout, verbose=False, callback_print_func=None):
        UdpIO.__init__(self, listen_port, desired_datagrams, timeout, verbose, callback_print_func)
        self.name = "SIP"
        self.cast = None

    def parse(self):
        self.cast = sippican.Sippican(self.data)
