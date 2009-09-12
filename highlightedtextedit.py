#!/usr/bin/env python

"""
highlightedtextedit.py

A PyQt custom widget example for Qt Designer.

Copyright (C) 2006 David Boddie <david@boddie.org.uk>
Copyright (C) 2005-2006 Trolltech ASA. All rights reserved.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

import os

from PyQt4 import QtCore, QtGui, uic

import conf

uidir = 'data/ui'

class TextEditor(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        uifile = 'editor.ui'
        uipath = os.path.join(uidir, uifile)
        TEClass, _ = uic.loadUiType(uipath)
        self.ui = TEClass()
        self.ui.setupUi(self)

        self.editor = HighlightedTextEdit(self.ui.centralwidget)
        self.ui.verticalLayout.addWidget(self.editor)
        self.setCentralWidget(self.ui.centralwidget)

        self._filepath = None

    def closeEvent(self, ev):
        if self.maybeSave():
            ev.accept()
        else:
            ev.ignore()

    def openfile(self, filepath=None):
        if filepath is None:
            filepath = conf.template
        else:
            self._filepath = filepath

        filestring = file(filepath).read()
        self.editor.code = filestring

        if filepath is None or filepath==conf.template:
            title = 'Untitled'
        else:
            _, title = os.path.split(str(filepath))
        self.setWindowTitle(title)

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def cut(self):
        self.editor.cut()

    def copy(self):
        self.editor.copy()

    def paste(self):
        self.editor.paste()

    def selectAll(self):
        self.editor.selectAll()

    def new(self):
        if self.maybeSave():
            self.openfile()

    def open(self):
        if self.maybeSave():
            fdir = QtCore.QString(os.path.abspath(conf.robot_dirs[0]))
            fp = QtGui.QFileDialog.getOpenFileName(self, 'Open Robot', fdir)
            if fp:
                self.openfile(fp)

    def save(self):
        if self._filepath is None:
            return self.saveAs()
        else:
            return self.savefile()

    def saveAs(self):
        fdir = QtCore.QString(os.path.abspath(conf.robot_dirs[0]))
        filepath = QtGui.QFileDialog.getSaveFileName(self, 'Save Robot As', fdir)
        if filename:
            self._filepath = filepath
            return self.savefile()
        else:
            return False

    def savefile(self):
        try:
            f = file(self._filepath, 'w')
            f.write(self.editor.code)
        except:
            QtGui.QMessageBox.warning(self, 'Cannot Save', 'Cannot save file')
            self._filepath = None
            return False
        else:
            self.editor._doc.setModified(False)
            return True

    def maybeSave(self):
        if self.editor._doc.isModified():
            ret = QtGui.QMessageBox.warning(self, self.tr("Application"),
                        self.tr("The document has been modified.\n"
                                "Do you want to save your changes?"),
                        QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                        QtGui.QMessageBox.No,
                        QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
            if ret == QtGui.QMessageBox.Yes:
                return self.save()
            elif ret == QtGui.QMessageBox.Cancel:
                return False
        return True



class HighlightedTextEdit(QtGui.QTextEdit):

    """HighlightedTextEdit(QtGui.QTextEdit)

    Provides a custom text editor with a simple built-in Python syntax
    highlighter.
    """

    def __init__(self, parent=None):

        QtGui.QTextEdit.__init__(self, parent)

        self.setFrameShape(QtGui.QFrame.Box)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        char_format = QtGui.QTextCharFormat()
        char_format.setFont(self.font())
        char_format.setFontPointSize(16)
        self.highlighter = PythonHighlighter(self.document(), char_format)
        self._doc = self.document()

        pal = QtGui.QPalette()
        bgc = QtGui.QColor(0, 0, 0)
        pal.setColor(QtGui.QPalette.Base, bgc)
        textc = QtGui.QColor(255, 255, 255)
        pal.setColor(QtGui.QPalette.Text, textc)
        self.setPalette(pal)

    # The code property is implemented with the getCode() and setCode()
    # methods, and contains the plain text shown in the editor.

    def getCode(self):
        self._code = self.toPlainText()
        return self._code

    def setCode(self, text):
        self.setPlainText(text)

    code = QtCore.pyqtProperty("QString", getCode, setCode)

    # The displayFont property is implemented with the getDisplayFont() and
    # setDisplayFont() methods, and contains the font used to display the
    # text in the editor.

    def getDisplayFont(self):
        return QtGui.QWidget.font(self)

    def setDisplayFont(self, font):
        QtGui.QWidget.setFont(self, font)
        self.highlighter.updateHighlighter(font)
        self.update()

    displayFont = QtCore.pyqtProperty("QFont", getDisplayFont, setDisplayFont)

    def keyPressEvent(self, ev):
        k = ev.key()

        if k == 16777217:
            spaces = QtCore.QString('    ')
            self.insertPlainText(spaces)

        else:
            QtGui.QTextEdit.keyPressEvent(self, ev)


class PythonHighlighter(QtGui.QSyntaxHighlighter):

    keywords = (
        "and",       "del",       "for",       "is",        "raise",
        "assert",    "elif",      "from",      "lambda",    "return",
        "break",     "else",      "global",    "not",       "try",
        "class",     "except",    "if",        "or",        "while",
        "continue",  "exec",      "import",    "pass",      "yield",
        "def",       "finally",   "in",        "print"
        )

    def __init__(self, document, base_format):

        QtGui.QSyntaxHighlighter.__init__(self, document)

        self.base_format = base_format
        self.document = document

        self.updateHighlighter(base_format.font())

    def highlightBlock(self, text):

        self.setCurrentBlockState(0)

        if text.trimmed().isEmpty():
            self.setFormat(0, len(text), self.empty_format)
            return

        self.setFormat(0, len(text), self.base_format)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = text.indexOf(self.multiLineStringBegin)

        if startIndex > -1:
            self.highlightRules(text, 0, startIndex)
        else:
            self.highlightRules(text, 0, len(text))

        while startIndex >= 0:

            endIndex = text.indexOf(self.multiLineStringEnd,
                startIndex + len(self.multiLineStringBegin.pattern()))
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = text.length() - startIndex
            else:
                commentLength = endIndex - startIndex + \
                                self.multiLineStringEnd.matchedLength()
                self.highlightRules(text, endIndex, len(text))

            self.setFormat(startIndex, commentLength, self.multiLineStringFormat)
            startIndex = text.indexOf(self.multiLineStringBegin,
                                      startIndex + commentLength)

    def highlightRules(self, text, start, finish):

        for expression, format in self.rules:

            index = expression.indexIn(text, start)
            while index >= start and index < finish:
                length = expression.matchedLength()
                self.setFormat(index, min(length, finish - index), format)
                index = expression.indexIn(text, index + length)

    def updateFonts(self, font):

        self.base_format.setFont(font)
        self.empty_format = QtGui.QTextCharFormat(self.base_format)

        self.keywordFormat = QtGui.QTextCharFormat(self.base_format)
        self.keywordFormat.setForeground(QtGui.QBrush(QtGui.QColor(116,167,255)))
        self.keywordFormat.setFontWeight(QtGui.QFont.Bold)
        self.callableFormat = QtGui.QTextCharFormat(self.base_format)
        self.callableFormat.setForeground(QtGui.QBrush(QtGui.QColor(116,255,87)))
        self.magicFormat = QtGui.QTextCharFormat(self.base_format)
        self.magicFormat.setForeground(QtGui.QColor(224,128,0))
        self.qtFormat = QtGui.QTextCharFormat(self.base_format)
        self.qtFormat.setForeground(QtCore.Qt.blue)
        self.qtFormat.setFontWeight(QtGui.QFont.Bold)
        self.selfFormat = QtGui.QTextCharFormat(self.base_format)
        self.selfFormat.setForeground(QtGui.QBrush(QtGui.QColor(255,127,127)))
        #self.selfFormat.setFontItalic(True)
        self.singleLineCommentFormat = QtGui.QTextCharFormat(self.base_format)
        self.singleLineCommentFormat.setForeground(QtGui.QBrush(QtGui.QColor(187,87,255)))
        self.multiLineStringFormat = QtGui.QTextCharFormat(self.base_format)
        self.multiLineStringFormat.setBackground(
            QtGui.QBrush(QtGui.QColor(127,127,255)))
        self.quotationFormat1 = QtGui.QTextCharFormat(self.base_format)
        self.quotationFormat1.setForeground(QtCore.Qt.yellow)
        self.quotationFormat2 = QtGui.QTextCharFormat(self.base_format)
        self.quotationFormat2.setForeground(QtCore.Qt.yellow)

    def updateRules(self):

        self.rules = []
        self.rules += map(lambda s: (QtCore.QRegExp(r"\b"+s+r"\b"),
                          self.keywordFormat), self.keywords)

        self.rules.append((QtCore.QRegExp(r"\b[A-Za-z_]+\(.*\)"), self.callableFormat))
        self.rules.append((QtCore.QRegExp(r"\b__[a-z]+__\b"), self.magicFormat))
        self.rules.append((QtCore.QRegExp(r"\bself\b"), self.selfFormat))
        self.rules.append((QtCore.QRegExp(r"\bQ([A-Z][a-z]*)+\b"), self.qtFormat))

        self.multiLineStringBegin = QtCore.QRegExp(r'\"\"\"')
        self.multiLineStringEnd = QtCore.QRegExp(r'\"\"\"')

        self.rules.append((QtCore.QRegExp(r"#[^\n]*"), self.singleLineCommentFormat))

        self.rules.append((QtCore.QRegExp(r'r?\"[^\n]*\"'), self.quotationFormat1))
        self.rules.append((QtCore.QRegExp(r"r?'[^\n]*'"), self.quotationFormat2))


    def updateHighlighter(self, font):

        self.updateFonts(font)
        self.updateRules()
        self.setDocument(self.document)


if __name__ == "__main__":

    import sys

    app = QtGui.QApplication(sys.argv)
    widget = HighlightedTextEdit()
    if len(sys.argv) == 2:
        fname = sys.argv[1]
        code = file(fname).read()
        widget.code = code
        g = QtCore.QRect(0, 0, 800, 600)
        widget.setGeometry(g)
    widget.show()
    sys.exit(app.exec_())
