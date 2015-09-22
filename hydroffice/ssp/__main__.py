from __future__ import absolute_import, division, print_function, unicode_literals

import wx
from .oldgui import svpeditor


def main():
    app = wx.App(False)
    svp_editor = svpeditor.SVPEditor(verbose=True)
    app.SetTopWindow(svp_editor)
    svp_editor.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()



