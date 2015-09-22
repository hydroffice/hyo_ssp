from __future__ import absolute_import, division, print_function, unicode_literals

from abc import ABCMeta, abstractmethod

from ..helper import SspError
from ...base.base_objects import BaseObject


class IoError(SspError):
    """
    Error raised for atlas issues
    """
    def __init__(self, message, *args):
        self.message = message
        # allow users initialize misc. arguments as any other builtin Error
        super(IoError, self).__init__(message, *args)


class BaseIo(BaseObject):
    """Common IO base class"""

    __metaclass__ = ABCMeta

    def __init__(self, verbose=False, callback_print_func=None):
        super(BaseIo, self).__init__(verbose=verbose, callback_print_func=callback_print_func)
        self.name = "BAS"

    @abstractmethod
    def listen(self):
        self.print_error("to be overloaded")