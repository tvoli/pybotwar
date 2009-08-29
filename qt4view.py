import os
import sys
import math
pi = math.pi
from PyQt4 import QtCore, QtGui, QtSvg, uic

import main
import world
import stats
import conf


def getrend(app):
    filename = 'robot.svg'
    filepath = os.path.join('data/images', filename)
    fp = QtCore.QString(filepath)
    rend = QtSvg.QSvgRenderer(fp, app)
    return rend

uidir = 'data/ui'
uifile = 'mainwindow.ui'
uipath = os.path.join(uidir, uifile)
MWClass, _ = uic.loadUiType(uipath)

nipath = os.path.join(uidir, uifile)
NIClass, _ = uic.loadUiType(uipath)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        self.paused = False

        QtGui.QMainWindow.__init__(self)
        self.ui = MWClass()
        self.ui.setupUi(self)

        self.scene = Scene()
        view = self.ui.arenaview
        view.setScene(self.scene)
        self.scene.view = view
        view.show()

        self.startTimer(17)

        self.game = main.Game()
        self.game.w.v.scene = self.scene
        self.game.w.v.app = app
        self.game.w.v.rinfo = self.ui.rinfo
        self.game.w.v.setrend()
        self.game.load_robots()

        # Call resize a bit later or else view will not resize properly
        QtCore.QTimer.singleShot(1, self.resizeEvent)

    def closeEvent(self, ev=None):
        self.game.finish()
        QtGui.qApp.quit()
        stats.dbclose()

    def pauseBattle(self, ev):
        self.paused = ev

    def singleStep(self):
        self.ui.actionPause.setChecked(True)
        self.pauseBattle(True)
        self.game.tick()

    def timerEvent(self, ev):
        if not self.paused:
            self.game.tick()

        if self.game.rnd > 60 * conf.maxtime:
            self.closeEvent()

        if len(self.game.procs) <= 1:
            self.closeEvent()

    def test(self):
        self.scene.r.set_rotation(self.rot)
        self.scene.r.set_position(self.pos)
        self.scene.r.set_turr_rot(self.turr_rot)

        self.rot += 1
        x, y = self.pos
        self.pos = x-2, y+1

        self.turr_rot -= 2

    def resizeEvent(self, ev=None):
        frect = self.ui.arenaframe.frameRect()
        sx, sy = frect.width(), frect.height()
        minsize = min((sx, sy))
        scale = 0.85*(minsize/600.)

        trans = QtGui.QTransform()
        trans.scale(scale, scale)
        self.scene.view.setTransform(trans)

    def configure(self):
        pass

    def loadRobot(self):
        pass

    def restart(self):
        pass


class Scene(QtGui.QGraphicsScene):
    def __init__(self):
        QtGui.QGraphicsScene.__init__(self)
        self.setSceneRect(-350, -350, 700, 700)
        color = QtGui.QColor(30, 30, 60)
        brush = QtGui.QBrush(color)
        self.setBackgroundBrush(brush)

        wcolor = QtGui.QColor(90, 90, 70)
        wbrush = QtGui.QBrush(wcolor)
        wpen = QtGui.QPen(wcolor)

        bpen = QtGui.QPen(wcolor)
        bpen.setWidth(30)
        bpen.setJoinStyle(2)
        ar = self.addRect(-300, -300, 600, 600)
        ar.setPen(bpen)
        bcolor = QtGui.QColor(40, 40, 70)
        ar.setBrush(bcolor)
        self.arenarect = ar


size = 30
def tl(pos):
    px, py =  pos
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
        self.icon = icon
        painter = QtGui.QPainter(icon)
        self.painter = painter # need to hold this or Qt throws an error
        imageid = 'r{0:02d}'.format(n)
        rend.render(painter, imageid)
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
        self.cx, self.cy = 45, 45

        GraphicsItem.__init__(self)

        self.item0 = scene.addEllipse(0, 0, 90, 90)
        self.item0.setParentItem(self)
        color = QtGui.QColor(250, 200, 0)
        brush = QtGui.QBrush(color)
        self.item0.setBrush(brush)

        self.item1 = scene.addEllipse(15, 15, 60, 60)
        self.item1.setParentItem(self)
        color = QtGui.QColor(200, 100, 100)
        brush = QtGui.QBrush(color)
        self.item1.setBrush(brush)
        self.item1.setParentItem(self.item0)

        self.item2 = scene.addEllipse(30, 30, 30, 30)
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
        self.rend = getrend(self.app)

    def addrobot(self, pos, ang):
        v = Robot(pos, ang, self.rend)
        self.scene.addItem(v)
        v.setParentItem(self.scene.arenarect)
        return v

    def addrobotinfo(self, n, name):
        ri = RobotInfo(n, name, self.rend)
        self.rinfo.addLayout(ri)
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
        rend = getrend(app)
        img = QtGui.QPixmap(500, 250)
        self.img = img
        painter = QtGui.QPainter(img)
        self.painter = painter # need to hold this or Qt throws an error
        rend.render(painter, 'splash')
        QtGui.QSplashScreen.__init__(self, img)



def run():
    app = QtGui.QApplication(sys.argv)

    splash = Splash(app)
    splash.show()

    import qt4view
    world.view = qt4view
    win = MainWindow(app)
    win.show()
    splash.finish(win)
    app.exec_()


if __name__ == "__main__":
    run()
