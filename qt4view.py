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
import sys
import math
pi = math.pi

import logging
logger = logging.getLogger('PybotwarLogger')

from PyQt4 import QtCore, QtGui, QtSvg, uic
from editor import TextEditor
from combatants import BattleEditor, TournamentEditor
from settings import Settings

import util
import stats
from about import AboutDialog
import conf


uidir = 'data/ui'
uifile = 'mainwindow.ui'
uipath = os.path.join(uidir, uifile)
MWClass, _ = uic.loadUiType(uipath)


class MainWindow(QtGui.QMainWindow):
    def __init__(self, app, testmode):
        self.app = app
        self.testmode = testmode
        self.paused = False
        self._tournament = None

        QtGui.QMainWindow.__init__(self)
        self.ui = MWClass()
        self.ui.setupUi(self)
        self.ui.nbattles_frame.hide()

        self.scene = Scene()
        view = self.ui.arenaview
        view.setScene(self.scene)
        self.scene.view = view
        view.show()

        self.start_game()

        self.debug_robot = None

        self.run_tournament(1)
        self.singleStep()

        self.ticktimer = self.startTimer(17)

        self.editors = []
        self._fdir = None

        self.setup_settings()

        # Call resize a bit later or else view will not resize properly
        self._initialresize = True
        QtCore.QTimer.singleShot(1, self.resizeEvent)

    def start_game(self):
        import game

        self.game = game.Game(self.testmode, self._tournament)
        self.game.w.v.scene = self.scene
        self.game.w.v.app = self.app
        self.game.w.v.rinfo = self.ui.rinfo
        self.game.w.v.setrend()
        self.game.load_robots()

        self.ui.countdown.display(conf.maxtime)

    def closeEvent(self, ev=None):
        self.killTimer(self.ticktimer)

        if len(self.game.procs) > 0:
            self.game.finish(False)
            stats.dbclose()

        doquit = True
        # Try to close any open editor windows
        for te in self.editors:
            if te.isVisible():
                te.close()

        # If any are still open, don't quit
        for te in self.editors:
            if te.isVisible():
                doquit = False

        if doquit:
            QtGui.qApp.quit()

    def startBattle(self):
        if self.paused:
            self.pauseBattle(False)

    def pauseBattle(self, ev):
        self.paused = ev
        if self.paused:
            self.ui.actionPause.setChecked(True)
            self.ui.actionStart_battle.setDisabled(False)
        else:
            self.ui.actionPause.setChecked(False)
            self.ui.actionStart_battle.setDisabled(True)

    def singleStep(self):
        self.pauseBattle(True)
        self.game.tick()
        if self.debug_robot is not None:
            self.update_debug_robot()

    def timerEvent(self, ev):
        if not self.paused:
            self.game.tick()
            if self.debug_robot is not None:
                self.update_debug_robot()

            if not self.game.rnd % 60:
                remaining = conf.maxtime - (self.game.rnd / 60)
                self.ui.countdown.display(remaining)

            if (self.game.rnd > 60 * conf.maxtime or
                    len(self.game.procs) <= 1):
                if not self.testmode:
                    self.battle_over()

    def battle_over(self):
        self.pauseBattle(True)
        self.game.finish()
        if self._supertournament_combos:
            if self._tournament_battles >= 1:
                self._tournament_battles -= 1
                self._supertournament_battles -= 1

            if self._tournament_battles:
                self.ui.nbattles.display(self._supertournament_battles)
                self.restart()
                self.paused = True
                self.startBattle()
            else:
                conf.robots = self._supertournament_combos.pop(0)
                self._tournament_battles = self._supertournament_nbattles
                self.ui.nbattles.display(self._supertournament_battles)
                self.restart()
                self.paused = True
                self.startBattle()

            if not self._supertournament_combos:
                self._supertournament_combos = None
                self._supertournament_battles = None
                self._supertournament_nbattles = None

        elif self._tournament:
            if self._tournament_battles >= 1:
                self._tournament_battles -= 1

            if self._tournament_battles:
                self.ui.nbattles.display(self._tournament_battles)
                self.restart()
                self.paused = True
                self.startBattle()
            else:
                self.ui.nbattles_frame.hide()
                self.sw = StatsWindow('Tournament Results')
                self.sw.tournament_results(self._tournament)
                self._tournament = None
                self.sw.show()

    def test(self):
        self.scene.r.set_rotation(self.rot)
        self.scene.r.set_position(self.pos)
        self.scene.r.set_turr_rot(self.turr_rot)

        self.rot += 1
        x, y = self.pos
        self.pos = x-2, y+1

        self.turr_rot -= 2

    def resizeEvent(self, ev=None):
        if self._initialresize:
            # Initial scaling comes out wrong for some reason. Fake it.
            scale = 0.66725
            self._initialresize = False
        else:
            frect = self.ui.arenaframe.frameRect()
            sx, sy = frect.width(), frect.height()
            minsize = min((sx, sy))
            scale = 0.85*(minsize/600.)

        trans = QtGui.QTransform()
        trans.scale(scale, scale)
        self.scene.view.setTransform(trans)

    def notImplementedYet(self):
        self.niy = NotImplementedYet()
        self.niy.show()

    def configure(self):
        self.sui = Settings()
        self.sui.show()

    def loadRobot(self, efdir=None):
        if efdir is not None:
            fdir = efdir
        elif self._fdir is None:
            fdir = QtCore.QString(os.path.abspath(conf.base_dir))
        else:
            fdir = self._fdir

        fp = QtGui.QFileDialog.getOpenFileName(self, 'Open file', fdir, 'Text files (*.py)')
        if fp:
            # Check to see if the file is already open in an editor
            for ed in self.editors:
                if ed._filepath == fp:
                    # If it is not visible, show it
                    if not ed.isVisible():
                        ed.show()
                    # raise the window and get out
                    ed.activateWindow()
                    ed.raise_()
                    return

            te = TextEditor(self)
            self.editors.append(te)
            te.openfile(fp)
            te.show()

            if efdir is None:
                # Opening from Main Window. Remember directory.
                self._fdir = te._fdir

    def newRobot(self):
        te = TextEditor(self)
        self.editors.append(te)
        te.openfile() # Open the template for a new robot
        te.show()

    def newBattle(self):
        self.com = BattleEditor(self)
        self.com.show()

    def newTournament(self):
        self.tournament = TournamentEditor(self)
        self.tournament.show()

    def run_tournament(self, nbattles, dt=None):
        if dt is None:
            import datetime
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._tournament = dt
        self._tournament_battles = nbattles
        self._supertournament_battles = None
        self._supertournament_nbattles = None
        self._supertournament_combos = None
        self.ui.nbattles.display(nbattles)
        self.ui.nbattles_frame.show()
        self.restart()
        self.paused = True
        self.startBattle()

    def run_supertournament(self, nbattles):
        import datetime
        dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        from itertools import combinations
        combos = []
        nrobots = len(conf.robots)
        for n in range(2, nrobots+1):
            combos.extend(combinations(conf.robots, n))
        self._tournament = dt
        self._tournament_battles = nbattles
        self._supertournament_nbattles = nbattles
        self._supertournament_battles = nbattles * len(combos)
        conf.robots = combos.pop(0)
        self._supertournament_combos = combos
        self.ui.nbattles.display(self._supertournament_battles)
        self.ui.nbattles_frame.show()
        self.restart()
        self.paused = True
        self.startBattle()

    def deleteLayoutItems(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayoutItems(item.layout())

    def restart(self):
        if self._tournament is None:
            self.run_tournament(1)
            return

        rinfo = self.ui.rinfo

        for name, robot in self.game.w.robots.items():
            robot.v.kill()

        self.game.finish(False)
        import world
        world.Robot.nrobots = 0
        Robot.nrobots = 0

        self.scene.removeItem(self.scene.arenarect)
        self.deleteLayoutItems(rinfo)

        self.scene.add_arenarect()
        self.start_game()

        paused = self.paused
        self.singleStep()
        self.pauseBattle(paused)

    def help(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl(conf.help_url))

    def about(self):
        AboutDialog(self.app).exec_()

    def setup_settings(self):
        self._fdir = conf.base_dir

    def enable_debug(self):
        if self.ui.actionEnableDebug.isChecked():
            self.game.enable_debug()
            self.ag = QtGui.QActionGroup(self.ui.menuDebug)
            self.ag.triggered.connect(self.choose_robot_debug)
            items = self.game.models.items()
            for robotname, model in items:
                ac = QtGui.QAction(robotname, self.ag)
                ac.setCheckable(True)
                self.ui.menuDebug.addAction(ac)
        else:
            self.game.disable_debug()
            for ac in self.ag.actions():
                self.ui.menuDebug.removeAction(ac)
            self.debug_robot = None

        self.singleStep()

    def choose_robot_debug(self):
        if self.debug_robot is not None:
            self.debug_robot_window.destroy()
            self.debug_robot_logfile.close()
        rname = self.ag.checkedAction().text()
        self.debug_robot = str(rname)
        self.debug_robot_window = RDebug(rname)
        self.debug_robot_window.show()
        logfilename = '%s.log' % rname
        logdir = os.path.join(conf.base_dir, conf.logdir)
        logfilepath = os.path.join(logdir, logfilename)
        logfile = open(logfilepath)
        self.debug_robot_logfile = logfile
        self.singleStep()

    def update_debug_robot(self):
        game = self.game
        model = game.models[self.debug_robot]
        body = model.body
        window = self.debug_robot_window

        tick = str(game.rnd)
        window.tick.setText(tick)

        health = max(int(model.health), 0)
        window.health.setValue(health)

        pos = body.position
        x, y = int(pos.x), int(pos.y)
        window.posx.setValue(x)
        window.posy.setValue(y)

        tur = str(model.get_turretangle())
        window.turret.setText(tur)

        pingtype = str(model._pingtype)
        pingangle = str(model._pingangle)
        pingdistance = str(model._pingdist)
        window.pingtype.setText(pingtype)
        window.pingangle.setText(pingangle)
        window.pingdistance.setText(pingdistance)

        gyro = str(model.gyro())
        window.gyro.setText(gyro)

        heat = int(model._cannonheat)
        window.cannonheat.setValue(heat)

        loading = str(model._cannonreload)
        window.cannonloading.setText(loading)

        pinged = str(model._pinged == game.rnd - 1)
        window.pinged.setText(pinged)

        for kind in [
                'FORCE',
                'TORQUE',
                'FIRE',
                'PING',
                'TURRET',
                'INACTIVE',
                ]:
            attr = 'c_%s' % kind
            attr = attr.lower()
            val = str(model._commands.get(kind, ''))
            getattr(window, attr).setText(val)

        while True:
            where = self.debug_robot_logfile.tell()
            line = self.debug_robot_logfile.readline()
            if not line:
                self.debug_robot_logfile.seek(where)
                break
            else:
                window.logarea.append(line.strip())

    def show_robot_stats(self):
        self.sw = StatsWindow('Robot Stats')
        self.sw.robot_stats()
        self.sw.show()

    def show_current_stats(self):
        self.sw = StatsWindow('Tournament Stats')
        self.sw.tournament_results(self._tournament)
        self.sw.show()

    def previous_tournaments(self):
        self.pt = TournamentStatsChooser()
        self.pt.show()
        

class RDebug(QtGui.QDialog):
    def __init__(self, rname):
        QtGui.QDialog.__init__(self)
        uifile = 'debug.ui'
        uipath = os.path.join(uidir, uifile)
        uic.loadUi(uipath, self)
        self.rname.setText(rname)


class NotImplementedYet(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        uifile = 'bd.ui'
        uipath = os.path.join(uidir, uifile)
        uic.loadUi(uipath, self)

    def accept(self):
        QtGui.QDialog.accept(self)

    def reject(self):
        QtGui.QDialog.reject(self)


class Scene(QtGui.QGraphicsScene):
    def __init__(self):
        QtGui.QGraphicsScene.__init__(self)
        self.setSceneRect(-350, -350, 700, 700)
        color = QtGui.QColor(30, 30, 60)
        brush = QtGui.QBrush(color)
        self.setBackgroundBrush(brush)
        self.add_arenarect()

    def add_arenarect(self):
        linecolor = QtGui.QColor(90, 90, 70)
        pen = QtGui.QPen(linecolor)
        pen.setWidth(30)
        pen.setJoinStyle(2)
        ar = self.addRect(-300, -300, 600, 600)
        ar.setPen(pen)
        bgcolor = QtGui.QColor(40, 40, 70)
        ar.setBrush(bgcolor)
        self.arenarect = ar


size = 30
def tl(pos):
    px, py =  pos.x, pos.y
    sz = size / 2
    x, y = (px*sz)-0, (py*sz)+0
    return x, y

class GraphicsItem(QtGui.QGraphicsItem):
    def __init__(self):
        QtGui.QGraphicsItem.__init__(self)

    def set_transform(self):
        cx, cy = self.cx, self.cy
        x, y = self.pos
        x -= cx
        y -= cy
        ang = self.ang

        trans = QtGui.QTransform()
        trans.translate(x, y)
        trans.translate(cx, cy).rotate(ang).translate(-cx, -cy)
        self.setTransform(trans)

    def setpos(self, pos):
        self.pos = pos
        self.set_transform()

    def set_rotation(self, ang):
        self.ang = -(180/pi)*ang
        self.set_transform()

    def rotate(self, deg):
        self.ang += deg
        self.set_transform()

    def paint(self, painter, option, widget):
        pass

    def kill(self):
        scene = self.item.scene()
        scene.removeItem(self.item)

class Robot(GraphicsItem):
    nrobots = 0
    def __init__(self, pos, ang, rend):
        Robot.nrobots += 1

        self.pos = tl(pos)
        self.ang = ang
        self.scale = 1
        self.cx, self.cy = 15, 15

        GraphicsItem.__init__(self)

        imageid = 'r{0:02d}'.format(Robot.nrobots)
        self.item = QtSvg.QGraphicsSvgItem(self)
        self.item.setSharedRenderer(rend)
        self.item.setElementId(imageid)

        self.turr = Turret(self, rend)

        self.set_transform()

    def setpos(self, pos):
        self.pos = tl(pos)
        self.set_transform()

    def boundingRect(self):
        return self.item.boundingRect()

    def set_turr_rot(self, ang):
        self.turr.set_rotation(ang)


class Turret(GraphicsItem):
    def __init__(self, robot, rend):
        self.pos = 15, 15
        self.ang = 0
        self.scale = 1
        self.cx, self.cy = 15, 15

        GraphicsItem.__init__(self)

        self.item = QtSvg.QGraphicsSvgItem(robot.item)
        self.item.setSharedRenderer(rend)
        self.item.setElementId('turret')
        self.set_transform()

    def set_transform(self):
        cx, cy = self.cx, self.cy
        x, y = self.pos
        x -= cx
        y -= cy
        ang = self.ang

        trans = QtGui.QTransform()
        trans.translate(x, y)
        trans.translate(cx, cy).rotate(ang).translate(-cx, -cy)
        self.item.setTransform(trans)


class Bullet(GraphicsItem):
    def __init__(self, pos, scene):
        self.pos = tl(pos)
        self.ang = 0
        self.scale = 1
        self.cx, self.cy = 2, 2

        GraphicsItem.__init__(self)

        self.item = scene.addEllipse(0, 0, 4, 4)
        self.item.setParentItem(self)
        color = QtGui.QColor(200, 200, 200)
        brush = QtGui.QBrush(color)
        self.item.setBrush(brush)
        self.set_transform()

    def setpos(self, pos):
        self.pos = tl(pos)
        self.set_transform()

    def boundingRect(self):
        return self.item.boundingRect()


class Wall(object):
    def __init__(self, pos, size):
        pass

class RobotInfo(QtGui.QHBoxLayout):
    def __init__(self, n, name, rend):
        QtGui.QHBoxLayout.__init__(self)

        icon = QtGui.QPixmap(50, 50)
        icon.fill(QtCore.Qt.transparent)
        self.icon = icon
        painter = QtGui.QPainter(icon)
        imageid = 'r{0:02d}'.format(n)
        rend.render(painter, imageid)
        painter.end()
        iconl = QtGui.QLabel()
        iconl.setPixmap(icon)

        vl = QtGui.QVBoxLayout()
        nm = QtGui.QLabel(name)
        nm.setFont(QtGui.QFont('Serif', 14))
        vl.addWidget(nm)

        self.health = Health()
        vl.addWidget(self.health)

        self.addWidget(iconl)
        self.addLayout(vl)

        #r = QtCore.QRect(0, 0, 300, 50)
        #self.setGeometry(r)



class Health(QtGui.QProgressBar):
    def __init__(self):
        QtGui.QProgressBar.__init__(self)
        self.setMaximum(conf.maxhealth)
        self.setMinimum(0)
        self._val = conf.maxhealth
        self.setValue(self._val)

    def step(self, n=None):
        if n is not None:
            self._val -= n
        else:
            self._val -= 1

        if self._val < 0:
            self._val = 0

        self.setValue(self._val)
        if self._val <= 0.30 * conf.maxhealth:
            pal = self.palette()
            pal.setColor(QtGui.QPalette.Highlight, QtGui.QColor('red'))
            self.setPalette(pal)

class Explosion(GraphicsItem):
    def __init__(self, pos, scene):
        self.pos = tl(pos)
        self.ang = 0
        self.scale = 1
        sizes = conf.explosion_radii

        maxsize = 15. * sizes[2]
        c = maxsize
        self.cx, self.cy = c, c

        GraphicsItem.__init__(self)

        s = 15. * sizes[2]
        self.item0 = scene.addEllipse(c-s, c-s, 2*s, 2*s)
        self.item0.setParentItem(self)
        color = QtGui.QColor(250, 200, 0)
        brush = QtGui.QBrush(color)
        self.item0.setBrush(brush)

        s = 15. * sizes[1]
        self.item1 = scene.addEllipse(c-s, c-s, 2*s, 2*s)
        self.item1.setParentItem(self)
        color = QtGui.QColor(200, 100, 100)
        brush = QtGui.QBrush(color)
        self.item1.setBrush(brush)
        self.item1.setParentItem(self.item0)

        s = 15. * sizes[0]
        self.item2 = scene.addEllipse(c-s, c-s, 2*s, 2*s)
        self.item2.setParentItem(self)
        color = QtGui.QColor(200, 50, 50)
        brush = QtGui.QBrush(color)
        self.item2.setBrush(brush)
        self.item2.setParentItem(self.item1)

        self.set_transform()

    def boundingRect(self):
        return self.item0.boundingRect()

    def setpos(self, pos):
        self.pos = tl(pos)
        self.set_transform()

    def set_rotation(self, ang):
        pass

    def kill(self):
        scene = self.item0.scene()
        scene.removeItem(self.item0)


class Arena(object):
    def setrend(self):
        svgrf = util.SvgRenderer(self.app)
        self.rend = svgrf.getrend()

    def addrobot(self, pos, ang):
        v = Robot(pos, ang, self.rend)
        self.scene.addItem(v)
        v.setParentItem(self.scene.arenarect)
        return v

    def addrobotinfo(self, n, name):
        ri = RobotInfo(n, name, self.rend)
        self.rinfo.addLayout(ri)
        #print 'rinfo22', self.rinfo
        #print 'ri', self.rinfo.geometry()
        return ri

    def addbullet(self, pos):
        v = Bullet(pos, self.scene)
        self.scene.addItem(v)
        v.setParentItem(self.scene.arenarect)
        return v

    def addexplosion(self, pos):
        e = Explosion(pos, self.scene)
        self.scene.addItem(e)
        e.setParentItem(self.scene.arenarect)
        return e

    def step(self, x=None):
        pass


class Splash(QtGui.QSplashScreen):
    def __init__(self, app):
        svgrf = util.SvgRenderer(app)
        rend = svgrf.getrend()
        img = QtGui.QPixmap(500, 250)
        img.fill(QtCore.Qt.transparent)
        self.img = img
        painter = QtGui.QPainter(img)
        rend.render(painter, 'splash')
        painter.end()
        QtGui.QSplashScreen.__init__(self, img, QtCore.Qt.WindowStaysOnTopHint)
        self.setMask(img.mask())
        self.away_later()

    def away_later(self):
        QtCore.QTimer.singleShot(2500, self.away)

    def away(self):
        if hasattr(self, 'win'):
            self.finish(self.win)
        else:
            self.away_later()

class TournamentStatsChooser(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle('Choose Tournament')
        self.vlayout = QtGui.QVBoxLayout()
        self.setLayout(self.vlayout)
        l, d = self.get_data()
        self.tournaments = l
        self.setup_table(l)
        self.fill_table(l, d)
        self.setGeometry(50, 50, 800, 400)

    def setup_table(self, data):
        l = len(data)
        w = 3
        self.tbl = QtGui.QTableWidget(l, w)
        self.tbl.cellClicked.connect(self.cellClicked)
        self.tbl.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        #hheader = self.tbl.horizontalHeader()
        #hheader.sectionClicked.connect(self.onHeaderClick)
        self.vlayout.addWidget(self.tbl)

    def get_data(self):
        l, d = stats.tournaments()
        return l, d

    def fill_table(self, l, d):
        for cn, header in enumerate(('Tournament', 'Robots', 'Matches')):
            item = QtGui.QTableWidgetItem(header)
            self.tbl.setHorizontalHeaderItem(cn, item)
        for rn, t in enumerate(l):
            robots = ', '.join(d[t]['robots'])
            complete = d[t]['complete']
            item = QtGui.QTableWidgetItem()
            item.setData(0, t)
            self.tbl.setItem(rn, 0, item)
            item = QtGui.QTableWidgetItem()
            item.setData(0, robots)
            self.tbl.setItem(rn, 1, item)
            item = QtGui.QTableWidgetItem()
            if complete:
                item.setData(0, d[t]['matches'])
            else:
                item.setData(0, 'incomplete')
            self.tbl.setItem(rn, 2, item)

        self.tbl.resizeColumnsToContents()

    def cellClicked(self, rn, cn):
        tournament = self.tournaments[rn]
        self.sw = StatsWindow(tournament)
        self.sw.tournament_results(tournament)
        self.sw.show()


class StatsWindow(QtGui.QDialog):
    def __init__(self, title):
        QtGui.QDialog.__init__(self)
        self.setWindowTitle(title)
        self.vlayout = QtGui.QVBoxLayout()
        self.setLayout(self.vlayout)
        self.setGeometry(50, 50, 900, 400)

    def setup_table(self, data):
        l = len(data)
        w = len(data[0]) - 1
        self.tbl = QtGui.QTableWidget(l, w)
        hheader = self.tbl.horizontalHeader()
        hheader.sectionClicked.connect(self.onHeaderClick)
        self.vlayout.addWidget(self.tbl)

    def setup_headers(self, headers):
        self.columnitems = {}
        for cn, header in enumerate(headers):
            item = QtGui.QTableWidgetItem(header)
            self.tbl.setHorizontalHeaderItem(cn, item)
            self.columnitems[item] = cn

    def fill_table(self, rows):
        self._name_map = {}
        for rn, row in enumerate(rows):
            nm = ''
            fp = ''
            for cn, i in enumerate(row):
                item = QtGui.QTableWidgetItem()

                if cn == 0:
                    nm = i
                elif cn == 1:
                    fp = i
                    self._name_map[fp] = nm

                try:
                    int(str(i))
                    item.setData(0, i)
                except ValueError:
                    try:
                        float(str(i))
                        i = round(i, 3)
                        item.setData(0, i)
                        label = QtGui.QLabel('%.3f' % i)
                        label.setStyleSheet("QLabel { background-color : white; color: black}")
                        self.tbl.setCellWidget(rn, cn-1, label)
                    except ValueError:
                        item = QtGui.QTableWidgetItem(i)
                        item.setData(0, i)

                if cn == 0:
                    self.tbl.setVerticalHeaderItem(rn, item)
                else:
                    self.tbl.setItem(rn, cn-1, item)

    def standard_headers(self):
        headers = [
            'fingerprint',
            'matches',
            'wins',
            'win pct',
            'opponents',
            'outlasted',
            'outlasted pct',
            'damage caused',
            'damage/match',
            'damage/opponent',
            'kills']
        self.setup_headers(headers)

    def tournament_results(self, dt):
        results = stats.get_tournament_stats(dt, sort='wpct DESC, opct DESC')
        if results:
            self.setup_table(results)
            self.standard_headers()
            self.fill_table(results)
        else:
            self.nothing_yet()

    def robot_stats(self):
        results = stats.get_robot_stats(sort='wpct DESC, opct DESC')
        if results:
            self.setup_table(results)
            self.standard_headers()
            self.fill_table(results)
        else:
            self.nothing_yet()

    def onHeaderClick(self, col):
        '''sort columns by clicked column value.

        Sorting of row headers depends on column 0 being unique.
            Works for standard_headers...
        '''
        self.tbl.sortItems(col, QtCore.Qt.DescendingOrder)
        for rn in range(self.tbl.rowCount()):
            fpi = self.tbl.item(rn, 0)
            fp = str(fpi.text())
            nm = self._name_map[fp]
            item = QtGui.QTableWidgetItem(nm)
            item.setData(0, nm)
            self.tbl.setVerticalHeaderItem(rn, item)

    def nothing_yet(self):
        lbl = QtGui.QLabel('Nothing yet')
        self.vlayout.addWidget(lbl)
            

def run(testmode):
    app = QtGui.QApplication(sys.argv)

    splash = Splash(app)
    splash.show()

    win = MainWindow(app, testmode)
    win.show()
    splash.win = win
    splash.raise_()
    app.exec_()


if __name__ == "__main__":
    import viewselect
    viewselect.select_view_module('pyqt')
    run(False)
    
