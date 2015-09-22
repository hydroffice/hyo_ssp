# -*- mode: python -*-
from PyInstaller import is_win, is_darwin

exe_file = 'SSP.out'
if is_win:
    exe_file = 'SSP.exe'
elif is_darwin:
    exe_file = 'SSP'

icon_file = 'SSP.ico'
if is_darwin:
    icon_file = 'SSP.icns'

block_cipher = None

patch_libs = []
if is_darwin:
    import os
    lib_path = os.path.abspath(os.path.join(os.path.dirname(os.__file__), os.pardir))
    patch_libs = [('libpng16.16.dylib', os.path.join(lib_path, 'libpng16.16.dylib'), 'BINARY'),
                  ('libQtGui.4.dylib', os.path.join(lib_path, 'libQtGui.4.8.6.dylib'), 'BINARY')]


a = Analysis(['SSP.py'],
             pathex=[''],
             binaries=None,
             datas=None,
             hiddenimports=['pkg_resources'],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)
media_tree = Tree('hydroffice/ssp/gui/media', prefix='hydroffice/ssp/gui/media')
manual_tree = Tree('hydroffice/ssp/docs', prefix='hydroffice/ssp/docs', excludes=['*.docx',])
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name=exe_file,
          debug=False,
          strip=None,
          upx=True,
          console=True, icon=icon_file)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
          	   media_tree,
               manual_tree,
               patch_libs,
               strip=None,
               upx=True,
               name='SSP')
