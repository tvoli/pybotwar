# Copyright 2010-2012 Lee Harr
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

from PyQt4 import QtGui, QtCore, uic

import util
version = 'pybotwar-0.9'

datadir = 'data'
uidir = os.path.join(datadir, 'ui')

class AboutDialog(QtGui.QDialog):
    def __init__(self, app):
        QtGui.QDialog.__init__(self)
        uifile = 'about.ui'
        uipath = os.path.join(uidir, uifile)
        self.ui = uic.loadUi(uipath, self)

        svgrenderer = util.SvgRenderer(app)
        rend = svgrenderer.getrend()
        img = QtGui.QPixmap(200, 100)
        img.fill(QtCore.Qt.transparent)
        self.img = img
        painter = QtGui.QPainter(img)
        rend.render(painter, 'splash')
        painter.end()

        self.ui.splasharea.setPixmap(self.img)
        self.ui.progtitle.setText(version)

