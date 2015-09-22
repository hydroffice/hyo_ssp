from __future__ import absolute_import, division, print_function, unicode_literals

import socket
import threading

from .base_io import BaseIo, IoError


class UdpIO(BaseIo):

    def __init__(self, listen_port, desired_datagrams, timeout, verbose=False, callback_print_func=None):
        super(UdpIO, self).__init__(verbose, callback_print_func)
        self.listen_port = listen_port
        self.desired_datagrams = desired_datagrams
        self.timeout = timeout
        self.verbose = verbose
        self.data = None
        self.sender = None
        self.sock_in = None

        # A few controls on behaviour
        self.do_listen = False
        self.listening = False

        # Goodies for logging to memory
        self.logging_to_memory = False
        self.logged_data = []

        # Goodies for logging to file
        self.logging_to_file = False
        self.logfile = None
        self.logfile_name = None

    def start_logging(self):
        """This method is meant to be over-ridden"""
        pass

    def stop_logging(self):
        """This method is meant to be over-ridden"""
        pass

    def clear_logged_data(self):
        self.logged_data = []

    def open_log_file(self, fname):
        self.logfile_name = fname
        self.logfile = open(fname, "wb")
        return

    def close_log_file(self):
        self.logfile.close()
        self.logfile = None
        self.logfile_name = None
        return

    def start_listen(self, logfilename=''):
        if logfilename != '':
            self.open_log_file(logfilename)
            self.logging_to_file = True

        self.listening = True
        self.print_info("starting listen thread")
        threading.Thread(target=self.listen).start()
        self.print_info("started listen thread")

    def listen(self):

        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_in.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 ** 16)

        if self.timeout > 0:
            self.sock_in.settimeout(self.timeout)

        try:
            self.sock_in.bind(("0.0.0.0", self.listen_port))

        except socket.error as e:
            self.listening = False
            self.sock_in.close()
            self.print_info("port %d already bound? Not listening anymore. Error: %s" % (self.listen_port, e))
            return

        self.print_info("going to listen on port %s for datagrams %s" % (self.listen_port, self.desired_datagrams))
        self.do_listen = True
        self.listening = True

        while self.do_listen:
            try:
                self.data, self.sender = self.sock_in.recvfrom(2 ** 16)

            except socket.timeout:
                # self.print_info("socket timeout")
                continue

            if self.verbose:
                port, ip = self.sender
                # print("Got data from %s (port: %s)" % (port, ip))
                # print(repr(self.data))

            if self.logging_to_file and self.logfile:
                self.print_info("going to write to output file %s length is %s bytes"
                                % (self.logfile_name, len(self.data)))

                self.log_to_file(self.data)

            if self.logging_to_memory:
                self.logged_data.append(self.data)

            self.parse()

        self.sock_in.close()

        self.print_info("done listening!")

    def stop_listen(self):
        self.do_listen = False

    def parse(self):
        return

    def log_to_file(self, data):
        self.logfile.write(data)
