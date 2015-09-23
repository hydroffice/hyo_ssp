# -*- mode: python -*-
from PyInstaller import is_win, is_darwin
from PyInstaller.building.datastruct import Tree
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, BUNDLE

import mpl_toolkits.basemap
import os
import sys


exe_file = 'SSP.out'
if is_win:
    exe_file = 'SSP.exe'
elif is_darwin:
    exe_file = 'SSP'

icon_file = 'SSP.ico'
if is_darwin:
    icon_file = 'SSP.icns'

# basemap data
src_basemap_data = os.path.join(mpl_toolkits.basemap.__path__[0], "data")
tgt_basemap_data = os.path.join('mpl_toolkits', 'basemap', 'data')
basemap_tree = Tree(src_basemap_data, prefix=tgt_basemap_data)

# gdal data (conda specific)
#src_gdal_data = os.path.join(os.path.dirname(sys.executable), 'lib', 'site-packages', 'osgeo', 'data', 'gdal')
src_gdal_data = os.path.join(os.path.dirname(sys.executable), 'Library', 'data')
tgt_gdal_data = os.path.join('Library', 'data')
gdal_tree = Tree(src_gdal_data, prefix=tgt_gdal_data)
src_prj_dll = os.path.join(os.path.dirname(sys.executable), 'proj.dll')
if not os.path.exists(src_prj_dll):
    raise RuntimeError(src_prj_dll)
prj_tree = [
    ('proj.dll', src_prj_dll, 'BINARY'),
]

# hydro-package data
media_tree = Tree('hydroffice/ssp/gui/media', prefix='hydroffice/ssp/gui/media')
manual_tree = Tree('hydroffice/ssp/docs', prefix='hydroffice/ssp/docs', excludes=['*.docx',])
pkg_data = [
    ('hydroffice/ssp/config.ini', 'hydroffice/ssp/config.ini', 'DATA'),
    ('hydroffice/ssp/oldgui/ccom.png', 'hydroffice/ssp/oldgui/ccom.png', 'DATA'),
    ('hydroffice/ssp/oldgui/favicon.ico', 'hydroffice/ssp/oldgui/favicon.ico', 'DATA')
]

# run the analysis
block_cipher = None
a = Analysis(['SSP.py'],
             pathex=[],
             #pathex=['C:\\hyo_dev\\_ssp'],
             binaries=None,
             datas=None,
             hiddenimports=['netCDF4.utils', 'netcdftime'],
             hookspath=None,
             runtime_hooks=None,
             excludes=None,
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

for d in a.binaries:
    if "system32\\pywintypes34.dll" in d[1]:
        a.binaries.remove(d)
    if "system32\\pywintypes27.dll" in d[1]:
        a.binaries.remove(d)

# a.binaries = [x for x in a.binaries if not x[0].startswith("scipy")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("IPython")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("zmq")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("OpenGL_accelerate")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("pandas")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("PyQt4")]
# a.binaries = [x for x in a.binaries if not x[0].startswith("pywintype27")]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          pkg_data,
          basemap_tree,
          gdal_tree,
          # prj_tree,
          media_tree,
          manual_tree,
          name=exe_file,
          debug=False,
          strip=None,
          upx=True,
          console=True, icon=icon_file)
if is_darwin:
    app = BUNDLE(exe,
                 name='SSP.app',
                 icon=icon_file,
                 bundle_identifier=None)
