from __future__ import absolute_import, division, print_function, unicode_literals

import datetime


class UserInputs(object):

    def __init__(self):

        # user insert
        self.user_speed = None
        self.user_salinity = None
        self.user_temperature = None
        self.user_depth = None

    def clear_user_samples(self):
        self.user_speed = None
        self.user_salinity = None
        self.user_temperature = None
        self.user_depth = None

    def __str__(self):
        output = " # User Inputs (time stamp: %s) #\n\n" % datetime.datetime.now().isoformat()

        output += "\n > User insert\n"
        output += "   - user_speed:  %s\n" % self.user_speed
        output += "   - user_salinity:  %s\n" % self.user_salinity
        output += "   - user_temperature:  %s\n" % self.user_temperature
        output += "   - user_depth:  %s\n" % self.user_depth

        return output
