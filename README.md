hyo_ssp
===========

The `hyo_ssp` package can be used as a starting point to build a hydro-package.

About HydrOffice
-----------------------

HydrOffice is a research development environment for ocean mapping. Its aim is to provide a collection of hydro-packages to deal with specific issues in such a field, speeding up both algorithms testing and research-2-operation.

About this hydro-package
-----------------------

This package provides functionalities to deal with sound speed profiles.

Freezing
-----------------------

### Pyinstaller

* `pyinstaller --clean -y -i SSP.ico --hidden-import=pkg_resources -F SSP.py`
* add `media_tree = Tree('hydroffice/ssp/gui/media', prefix='hydroffice/ssp/gui/media')`
* add `manual_tree = Tree('hydroffice/ssp/docs', prefix='hydroffice/ssp/docs', excludes=['*.docx',])`
* `pyinstaller --clean -y SSP.spec`

Useful Mercurial commands
-----------------------

### Merge a branch to default

* `hg update default`
* `hg merge 1.0.0`
* `hg commit -m"Merged 1.0.2 branch with default" -ugiumas`
* `hg update 1.0.0`
* `hg commit -m"Close 1.0.2 branch" -ugiumas --close-branch`

### Open a new branch

* `hg update default`
* `hg branch 1.0.1`
* `hg commit -m"Created 1.0.3 branch" -ugiumas`
    
Other info
----------

* Bitbucket: https://bitbucket.org/gmasetti/hyo_ssp
* Project page: http://ccom.unh.edu/project/hydroffice
* License: BSD-like license (See COPYING)