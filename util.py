# Copyright 2009-2014 Lee Harr
#
# This file is part of pybotwar.
#     http://pybotwar.googlecode.com/
#
# Pybotwar is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pybotwar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pybotwar.  If not, see <http://www.gnu.org/licenses/>.


import os


def makeconf():
    'create an empty conf file'

    conf_file = 'conf.py'

    if os.path.exists(conf_file):
        print 'conf.py already exists'
        raise SystemExit

    contents = '''\
# Change configuration settings here.
# See defaults.py for the default settings

from defaults import *


'''

    f = open(conf_file, 'w')
    f.write(contents)
    f.close()

    print 'conf.py created'
    print 'please check configuration.'


from collections import defaultdict

class defaultNonedict(defaultdict):
    def __missing__(self, key):
        return None


def get_robot_dirs():
    import conf

    base = conf.base_dir
    dirs = [base]

    for d in conf.more_robot_dirs:
        if os.path.isabs(d):
            dirs.append(d)
        else:
            dirs.append(os.path.join(base, d))
    
    return dirs


def setup_qt_settings():
    import settings
    settings.setup_qt_settings()
    settings.load_robots()


def setup_conf():
    import conf
    if conf.use_qt_settings:
        setup_qt_settings()

    
class SvgRenderer(object):
    'factory for svg renderer objects'

    def __init__(self, app):
        self.app = app

    def getrend(self, filepath=None):
        '''return a handle to the shared SVG renderer
            for the given svg file.

        If no filepath is given, return the renderer for
            the default svg file.

        '''

        from PyQt4 import QtCore, QtSvg

        if filepath is None:
            datadir = 'data'
            filename = 'robot.svg'
            filepath = os.path.join(datadir, 'images', filename)
        fp = QtCore.QString(filepath)
        rend = QtSvg.QSvgRenderer(fp, self.app)
        return rend

