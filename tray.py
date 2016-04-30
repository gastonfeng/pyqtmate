#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
import threading

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        #设置一个iconComboBox
        self.iconComboBox = QtGui.QComboBox()
        self.iconComboBox.addItem(
            QtGui.QIcon('favicon.ico'), "Dmyz")
#-------------------通知区域图标右键菜单start------------------
        self.minimizeAction = QtGui.QAction(u"最小化", self,
                triggered=self.hide)
        self.restoreAction = QtGui.QAction(u"&amp;显示窗口", self,
                triggered=self.showNormal)
        self.quitAction = QtGui.QAction(u"&amp;退出", self,
                triggered=QtGui.qApp.quit)
        #弹出的菜单的行为，包括退出，还原，最小化
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.restoreAction)
        self.trayIconMenu.addAction(self.minimizeAction)
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
#-------------------通知区域图标右键菜单end------------------
        #设置通知区域的ICON
        self.iconComboBox.currentIndexChanged.connect(
            self.setIcon)

        #通知区域icon显示
        self.iconComboBox.setCurrentIndex(1)
        self.trayIcon.show()
        self.trayIcon.activated.connect(
            self.iconActivated)

        #设定弹出主窗口的标题和大小
        self.setWindowTitle(u"动漫驿站通知程序")
        self.resize(400, 300)

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger,
                      QtGui.QSystemTrayIcon.DoubleClick):
            self.showNormal()
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def setIcon(self, index):
        icon = self.iconComboBox.itemIcon(0)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip(
            self.iconComboBox.itemText(index))

    def showMessage(self):
        #这里是可以设置弹出对话气泡的icon的，作为实验就省略了
        icon = QtGui.QSystemTrayIcon.MessageIcon()
        self.trayIcon.showMessage(
            u'提示',u'您有新的任务，请注意查收', icon,1000)

    def getTasksNum(self):
        self.showMessage()

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    window = Window()
    window.getTasksNum()

    sys.exit(app.exec_())