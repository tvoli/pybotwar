import sys
from PyQt4 import QtCore, QtGui, QtSvg, uic

uifile = 'vbox.ui'
MWClass, _ = uic.loadUiType(uifile)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.ui = MWClass()
        self.ui.setupUi(self)

        filename = 'star.svg'
        filestring = QtCore.QString(filename)
        rend = QtSvg.QSvgRenderer(filestring, app)

        self.star = QtGui.QPixmap(50, 50)
        self.painter = QtGui.QPainter(self.star)
        imageid = 'star'
        rend.render(self.painter, imageid)
        self.starlabel = QtGui.QLabel()
        self.starlabel.setPixmap(self.star)
        self.ui.vbox.addWidget(self.starlabel)

def run():
    app = QtGui.QApplication(sys.argv)
    win = MainWindow(app)
    win.show()
    app.exec_()

if __name__ == "__main__":
    run()
