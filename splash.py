# coding=utf-8
import sys
import threading

from PyQt4 import QtGui
from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QMainWindow

from guiqt import guiqt
#from uisplash import Ui_MainWindow


class qtsplash(guiqt):
    start=pyqtSignal(list)
    def __init__(self, mainProg, *args):
        guiqt.__init__(self,'splash', *args)
        self.setWindowFlags(Qt.SplashScreen)
        self.progressBar.setTextVisible(False)
        self.show()
        self.start.connect(mainProg)
        self.start.emit([self,])
        #mainProg(self)

    def msg(self, msg, step, steps):
        self.label_msg.setText(msg)
        self.progressBar.setRange(0,steps)
        self.progressBar.setValue(step)
