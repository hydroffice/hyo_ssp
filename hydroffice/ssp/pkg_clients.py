from __future__ import absolute_import, division, print_function, unicode_literals

from ..base.base_objects import BaseObject
from .ssp_dicts import Dicts


class PkgClient(BaseObject):
    def __init__(self, client, verbose=False, callback_print_func=None):
        super(PkgClient, self).__init__(verbose=verbose, callback_print_func=callback_print_func)
        self.name = "CLN"

        self.name = client.split(":")[0]
        self.IP = client.split(":")[1]
        self.port = int(client.split(":")[2])
        self.protocol = client.split(":")[3]
        self.alive = True
        self.print_info(" new client: %s(%s:%s) %s" % (self.name, self.IP, self.port, self.protocol))

    def send_cast(self, ssp_data, fmt):

        if self.protocol == "QINSY" or self.protocol == "PDS2000":
            fmt = Dicts.kng_formats['S12']
            self.print_info("forcing S12 format")

        if self.protocol == "QINSY" or self.protocol == "SIS" or self.protocol == "PDS2000":
            self.print_info("sending by km function")
            ssp_data.send_km(self.IP, self.port, fmt)

        elif self.protocol == "HYPACK":
            self.print_info("sending by hypack function")
            ssp_data.send_hypack(self.IP, self.port)


class PkgClientList(object):
    def __init__(self):
        self.num_clients = 0
        self.clients = []

    def add_client(self, client):
        client = PkgClient(client)
        self.clients.append(client)
        self.num_clients += 1
