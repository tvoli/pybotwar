#!/usr/bin/env python

# Copyright 2009 Lee Harr
#
# This file is part of pybotwar.
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
import sys
import glob

from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import QFrame, QWidget, QHBoxLayout, QPainter

import conf

import highlightedtextedit
import numberedtextedit

uidir = 'data/ui'

class CombatantsEditor(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uifile = 'combatants.ui'
        uipath = os.path.join(uidir, uifile)
        CEClass, _ = uic.loadUiType(uipath)
        self.ui = CEClass()
        self.ui.setupUi(self)
        self.show_selected()
        self.show_available()

    def show_available(self):
        available = set()
        for d in conf.robot_dirs:
            g = '%s/*.py' % d
            found = glob.glob(g)
            available.update(found)

        for robotpath in available:
            d, filename = os.path.split(robotpath)
            robotname = filename[:-3]
            if not self.ui.selectedrobots.findItems(robotname, QtCore.Qt.MatchExactly):
                item = QtGui.QListWidgetItem(robotname, self.ui.availablerobots)


    def show_selected(self):
        for robotname in conf.robots:
            item = QtGui.QListWidgetItem(robotname, self.ui.selectedrobots)
