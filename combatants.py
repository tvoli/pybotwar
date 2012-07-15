# Copyright 2009-2012 Lee Harr
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
import sys
import glob

from PyQt4 import QtCore, QtGui, uic
from PyQt4.Qt import QFrame, QWidget, QHBoxLayout, QPainter

import util
import conf

uidir = 'data/ui'

class CombatantsEditor(QtGui.QMainWindow):
    def __init__(self, parent):
        self.parent = parent
        QtGui.QMainWindow.__init__(self)
        uifile = 'combatants.ui'
        uipath = os.path.join(uidir, uifile)
        CEClass, _ = uic.loadUiType(uipath)
        self.ui = CEClass()
        self.ui.setupUi(self)
        self.setWindowTitle('Start Battle')
        self.show_selected()
        self.show_available()
        self.setup_lineups_dir()

    def show_available(self):
        available = self.ui.availablerobots
        selected = self.ui.selectedrobots
        robotpaths = set()
        rdirs = util.get_robot_dirs()
        for d in rdirs:
            g = '%s/*.py' % d
            found = glob.glob(g)
            found = [f for f in found if conf.template not in f]
            robotpaths.update(found)

        for robotpath in robotpaths:
            d, filename = os.path.split(robotpath)
            robotname = filename[:-3]
            if not available.findItems(robotname, QtCore.Qt.MatchExactly):
                item = QtGui.QListWidgetItem(robotname, available)

    def is_available(self, robotname):
        for d in util.get_robot_dirs():
            fname = '%s.py' % robotname
            fpath = os.path.join(d, fname)
            if os.path.exists(fpath):
                return True
        return False

    def show_selected(self):
        selected = self.ui.selectedrobots
        for robotname in conf.robots:
            if self.is_available(robotname):
                item = QtGui.QListWidgetItem(robotname, selected)

    def addrobot(self):
        available = self.ui.availablerobots
        selected = self.ui.selectedrobots
        for item in available.selectedItems():
            name = str(item.text())
            newitem = QtGui.QListWidgetItem(name, selected)

    def removerobot(self):
        available = self.ui.availablerobots
        selected = self.ui.selectedrobots
        for item in selected.selectedItems():
            name = str(item.text())
            row = selected.row(item)
            selected.takeItem(row)
            found = available.findItems(name, QtCore.Qt.MatchExactly)
            if not found:
                available.addItem(item)

    def removeall(self):
        selected = self.ui.selectedrobots
        while selected.count():
            item = selected.item(0)
            selected.setItemSelected(item, True)
            self.removerobot()

    def setup_lineups_dir(self):
        ldir = os.path.join(conf.base_dir, conf.lineups)
        if not os.path.exists(ldir):
            os.mkdir(ldir)
        self._fdir = ldir

    def save(self):
        robots = self.getselected()

        filepath = QtGui.QFileDialog.getSaveFileName(self, 'Save Battle Lineup As', self._fdir)
        if not filepath:
            return

        f = file(filepath, 'w')
        for name in robots:
            f.write(name)
            f.write('\n')

        return f

    def load(self):
        available = self.ui.availablerobots
        fdir = QtCore.QString(os.path.abspath(conf.lineups))
        fp = QtGui.QFileDialog.getOpenFileName(self, 'Open Battle Lineup', self._fdir)
        if fp:
            self.removeall()
            f = file(fp)

            items = []
            not_available = []
            for line in f:
                name = line.strip()
                if name.startswith('NBATTLES'):
                    self.set_nbattles(name)
                    continue
                found = available.findItems(name, QtCore.Qt.MatchExactly)
                if not found:
                    not_available.append(name)
                else:
                    item = found[0]
                    items.append(item)

            if not_available:
                self.robots_not_found(not_available)
            else:
                for item in items:
                    available.setItemSelected(item, True)
                    self.addrobot()

    def robots_not_found(self, not_available):
        text = 'Robot code not found:\n'
        lines = '\n'.join(not_available)
        warn = QtGui.QMessageBox.warning(self, 'Not Found', text+lines)

    def getselected(self):
        selected = self.ui.selectedrobots
        robots = []
        for i in range(selected.count()):
            item = selected.item(i)
            name = str(item.text())
            robots.append(name)
        return robots

    def save_to_settings(self, robots):
        if conf.use_qt_settings:
            import settings
            settings.save_robots(robots)


class BattleEditor(CombatantsEditor):
    def __init__(self, parent):
        CombatantsEditor.__init__(self, parent)
        self.setWindowTitle('Start Battle')
        self.ui.startbutton.setText('Start Battle')

    def save(self):
        f = CombatantsEditor.save(self)
        if f:
            f.close()

    def set_nbattles(self, line):
        pass

    def start(self):
        robots = self.getselected()
        conf.robots = robots
        self.save_to_settings(robots)
        self.parent.restart()
        self.parent.paused = True
        self.close()
        self.parent.startBattle()


class TournamentEditor(CombatantsEditor):
    def __init__(self, parent):
        CombatantsEditor.__init__(self, parent)
        self.setWindowTitle('Start Tournament')
        self.ui.startbutton.setText('Start Tournament')

        nbattles_layout = QtGui.QHBoxLayout()
        nbattles_layout.insertStretch(0, 0)
        nbattles_layout.addWidget(QtGui.QLabel('Number of battles'))
        self.nbattles = QtGui.QSpinBox(self)
        self.nbattles.setMinimum(1)
        nbattles_layout.addWidget(self.nbattles)
        self.ui.additional.addLayout(nbattles_layout)

    def save(self):
        f = CombatantsEditor.save(self)
        if f:
            f.write('NBATTLES %s\n' % self.nbattles.value())
            f.close()

    def set_nbattles(self, line):
        _, n = line.split()
        self.nbattles.setValue(int(n))

    def start(self):
        robots = self.getselected()
        conf.robots = robots
        self.save_to_settings(robots)
        self.parent.run_tournament(self.nbattles.value())
        self.close()

