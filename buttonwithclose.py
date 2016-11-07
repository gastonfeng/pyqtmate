from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

from guiqt import ui_compile

ui_compile('buttonwc')
from uibuttonwc import Ui_Form


class buttonwc(QtGui.QFrame, Ui_Form):
    Cilcked = pyqtSignal()
    Closed = pyqtSignal()

    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)
        self.setupUi(self)

    def setText(self, txt):
        self.pushButton.setText(txt)

    def on_pushButton_clicked(self, b):
        self.Clicked()

    def on_toolButton_clicked(self):
        self.Closed.emit()
