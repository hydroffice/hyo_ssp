from __future__ import absolute_import, division, print_function

import wx
from . import svpeditor


def gui():
    app = wx.App(False)
    svp_editor = svpeditor.SVPEditor(verbose=True)
    app.SetTopWindow(svp_editor)
    svp_editor.Show()
    app.MainLoop()