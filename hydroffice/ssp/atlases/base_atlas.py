from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod

from ..helper import SspError
from ...base.base_objects import BaseObject
from ...base.geodesy import Geodesy


class AtlasError(SspError):
    """
    Error raised for atlas issues
    """
    def __init__(self, message, *args):
        self.message = message
        # allow users initialize misc. arguments as any other builtin Error
        super(AtlasError, self).__init__(message, *args)


class Atlas(BaseObject):
    """Common atlas base class"""

    __metaclass__ = ABCMeta

    def __init__(self, verbose=False, callback_print_func=None):
        super(Atlas, self).__init__(verbose=verbose, callback_print_func=callback_print_func)
        self.name = "ATL"
        self.source_info = "Unknown Atlas"

        self.g = Geodesy()

    @abstractmethod
    def query(self, latitude, longitude, date_time):
        self.print_error("to be overloaded")