import os
import sys
from PyQt4 import QtCore, QtGui, QtSvg


def setrend(app):
    filename = 'robot.svg'
    filepath = os.path.join('data/images', filename)
    fp = QtCore.QString(filepath)
    global rend
    rend = QtSvg.QSvgRenderer(fp, app)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #self.resize(800, 600)

        fileMenu = QtGui.QMenu(self.tr("&File"), self)
        self.openAction = fileMenu.addAction(self.tr("&Open..."))
        self.openAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O")))
        self.quitAction = fileMenu.addAction(self.tr("E&xit"))
        self.quitAction.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self.connect(self.quitAction, QtCore.SIGNAL("triggered()"), QtGui.qApp, QtCore.SLOT("quit()"))

        self.menuBar().addMenu(fileMenu)

        self.scene = Scene()
        self.setCentralWidget(self.scene.view)

        self.startTimer(17)

        self.rot = 0
        self.pos = (0, 0)
        self.turr_rot = 0

    def timerEvent(self, ev):
        self.tick()

    def tick(self):
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
        w = self.addRect(-400, -300, 10, 600)
        w.setBrush(wbrush)
        w.setPen(wpen)
        w = self.addRect(-400, -300, 600, 10)
        w.setBrush(wbrush)
        w.setPen(wpen)
        w = self.addRect(190, -300, 10, 600)
        w.setBrush(wbrush)
        w.setPen(wpen)
        w = self.addRect(-400, 290, 600, 10)
        w.setBrush(wbrush)
        w.setPen(wpen)

        r = Robot((100, 100), 30)
        self.addItem(r)
        self.r = r

        view = QtGui.QGraphicsView(self)
        view.resize(800, 600)
        view.show()
        view.scale(.9, .9)
        self.view = view

class GraphicsItem(QtGui.QGraphicsItem):
    def __init__(self):
        QtGui.QGraphicsItem.__init__(self)

    def set_transform(self):
        cx, cy = self.cx, self.cy
        x, y = self.pos
        x -= cx
        y -= cy
        ang = self.ang
        scale = self.scale

        trans = QtGui.QTransform()
        trans.scale(scale, scale)
        trans.translate(x, y)
        trans.translate(cx, cy).rotate(ang).translate(-cx, -cy)
        self.item.setTransform(trans)

    def set_position(self, pos):
        self.pos = pos
        self.set_transform()

    def set_rotation(self, ang):
        self.ang = ang
        self.set_transform()

    def rotate(self, deg):
        self.ang += deg
        self.set_transform()

    def paint(self, painter, option, widget):
        pass

class Robot(GraphicsItem):
    nrobots = 0
    def __init__(self, pos, ang):
        Robot.nrobots += 1

        self.pos = pos
        self.ang = ang
        self.scale = .30
        self.cx, self.cy = 50, 50

        GraphicsItem.__init__(self)

        imageid = 'r{0:02d}'.format(Robot.nrobots)
        self.item = QtSvg.QGraphicsSvgItem(self)
        self.item.setSharedRenderer(rend)
        self.item.setElementId(imageid)

        self.turr = Turret(self)

        self.set_transform()

    def boundingRect(self):
        return self.item.boundingRect()

    def set_turr_rot(self, ang):
        self.turr.set_rotation(ang)


class Turret(GraphicsItem):
    def __init__(self, robot):
        self.pos = 50, 50
        self.ang = 0
        self.scale = 1
        self.cx, self.cy = 50, 50

        GraphicsItem.__init__(self)

        self.item = QtSvg.QGraphicsSvgItem(robot.item)
        self.item.setSharedRenderer(rend)
        self.item.setElementId('turret')
        self.set_transform()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    setrend(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
