import os
import sys
from PyQt4 import QtCore, QtGui, QtSvg


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


    def resizeEvent(self, ev):
        self.scene.r.body.rotate(5)
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

        filename = 'robot.svg'
        filepath = os.path.join('data/images', filename)
        fp = QtCore.QString(filepath)
        renderer = QtSvg.QSvgRenderer(fp, app)

        r = Robot((100, 100), 30, renderer)
        r.setPos(-100, -100)
        self.addItem(r)
        self.r = r

        view = QtGui.QGraphicsView(self)
        view.resize(800, 600)
        view.show()
        view.scale(.9, .9)
        self.view = view

        fitr = QtCore.QRectF(-400, -300, 800, 600)
        self.view.fitInView(fitr)


class Robot(QtGui.QGraphicsItem):
    nrobots = 0
    def __init__(self, pos, ang, rend):
        QtGui.QGraphicsItem.__init__(self)
        Robot.nrobots += 1
        imageid = 'r{0:02d}'.format(Robot.nrobots)
        self.body = QtSvg.QGraphicsSvgItem(self)
        self.body.setSharedRenderer(rend)
        self.body.setElementId(imageid)
        self.body.scale(.25, .25)
        self.body.rotate(125)

        self.turr = QtSvg.QGraphicsSvgItem(self.body)
        self.turr.setSharedRenderer(rend)
        self.turr.setElementId('turret')
        self.turr.setPos(-10, 10)
        self.turr.scale(.4, .4)
        #self.turr.rotate(5)

    def paint(self, painter, option, widget):
        print 'paint'


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
