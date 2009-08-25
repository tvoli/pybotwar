import os
import sys
import math
pi = math.pi
from PyQt4 import QtCore, QtGui, QtSvg

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


class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle('pybotwar')

        fileMenu = QtGui.QMenu(self.tr("&File"), self)
        self.openAction = fileMenu.addAction(self.tr("&Open..."))
        self.openAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O")))
        self.quitAction = fileMenu.addAction(self.tr("E&xit"))
        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.connect(self.quitAction, QtCore.SIGNAL("triggered()"), self.closeEvent)

        self.menuBar().addMenu(fileMenu)

        self.scene = Scene()
        self.setCentralWidget(self.scene.view)

        self.startTimer(17)

        self.game = main.Game()
        self.game.w.v.scene = self.scene
        self.game.w.v.app = app
        self.game.w.v.setrend()
        self.game.load_robots()

    def closeEvent(self, ev=None):
        self.game.finish()
        QtGui.qApp.quit()
        stats.dbclose()

    def timerEvent(self, ev):
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

    def resizeEvent(self, ev):
        os = ev.oldSize()
        ox, oy = os.width(), os.height()
        if ox < 0:
            ox, oy = self.width(), self.height()
        s = ev.size()
        sx, sy = s.width(), s.height()
        scale = 1.2*(float(sy)/800)
        print scale

        trans = QtGui.QTransform()
        trans.scale(scale, scale)
        self.scene.view.setTransform(trans)

class Scene(QtGui.QGraphicsScene):
    def __init__(self):
        QtGui.QGraphicsScene.__init__(self)
        self.setSceneRect(-400, -300, 800, 600)
        color = QtGui.QColor(40, 40, 70)
        brush = QtGui.QBrush(color)
        self.setBackgroundBrush(brush)

        wcolor = QtGui.QColor(90, 90, 70)
        wbrush = QtGui.QBrush(wcolor)
        wpen = QtGui.QPen(wcolor)

        bpen = QtGui.QPen(wcolor)
        bpen.setWidth(30)
        bpen.setJoinStyle(2)
        w = self.addRect(-400, -300, 600, 600)
        w.setPen(bpen)

        view = QtGui.QGraphicsView(self)
        view.resize(800, 600)
        view.show()
        view.scale(.9, .9)
        self.view = view

size = 30
def tl(pos):
    px, py =  pos
    sz = size / 2
    x, y = (px*sz)-100, (py*sz)+0
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

class RobotInfo(object):
    def __init__(self, n, name):
        self.health = Health()

class Health(object):
    def step(self, n=None):
        pass

class Explosion(object):
    def __init__(self, a=None, b=None):
        pass

    def setpos(self, pos):
        pass

    def set_rotation(self, ang):
        pass

    def kill(self):
        pass

class Arena(object):
    def setrend(self):
        self.rend = getrend(self.app)

    def addrobot(self, pos, ang):
        v = Robot(pos, ang, self.rend)
        self.scene.addItem(v)
        return v

    def addrobotinfo(self, n, name):
        return RobotInfo(n, name)

    def addbullet(self, pos):
        v = Bullet(pos, self.scene)
        self.scene.addItem(v)
        return v

    def addexplosion(self, pos):
        e = Explosion(pos)
        return e

    def step(self, x=None):
        pass


def run():
    app = QtGui.QApplication(sys.argv)

    filename = 'splash.png'
    filepath = os.path.join('data/images', filename)
    fp = QtCore.QString(filepath)
    splashpixmap = QtGui.QPixmap(fp)
    splash = QtGui.QSplashScreen(splashpixmap)
    splash.show()

    import qt4view
    world.view = qt4view
    win = MainWindow(app)
    win.show()
    splash.finish(win)
    app.exec_()


if __name__ == "__main__":
    run()
