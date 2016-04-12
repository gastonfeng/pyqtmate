# -*- coding: utf-8 -*-
from PyQt4 import QtGui, uic


class dialogVerimg(QtGui.QDialog):
    def __init__(self, ui, *args):
        QtGui.QDialog.__init__(self, *args)
        self.win = uic.loadUi('verimg.ui', self)
        self.exec_()

    def accept(self):
        return True, self.win.lineEdit.text()
