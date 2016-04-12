from PyQt4 import QtGui


class qpushbutton(QtGui.QPushButton):
    def __init__(self, *args):
        QtGui.QPushButton.__init__(self, *args)
        self.data=False



