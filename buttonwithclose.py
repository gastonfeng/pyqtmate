from PyQt4 import QtGui

from guiqt import ui_compile

ui_compile('buttonwc')
from uibuttonwc import Ui_Form
class buttonwc(QtGui.QFrame,Ui_Form):
    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)
        self.setupUi(self)

    def setText(self,txt):
        self.pushButton.setText(txt)