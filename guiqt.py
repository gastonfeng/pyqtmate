# coding=utf-8
import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import QFile
from PyQt4.QtGui import QAbstractItemView

from QTwrap import qtmodel, qtMenu, qtTreeModel

"""编译UI文件"""


def ui_compile(uifile):
    if os.path.isfile(uifile + '.ui'):
        ui = QFile(uifile + '.ui')
        py = QFile('ui' + uifile + '.py')
        ui.open(QFile.ReadOnly)
        py.open(QFile.WriteOnly)
        uic.compileUi(ui, py)
        ui.close()
        py.close()


class guiqt(QtGui.QMainWindow):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.setupUi(self)
        self.show()
        # self.win = uic.loadUi(ui, self)

    def load_buttons(self, buttons):
        for btn in buttons:
            btn['widget'].clicked.connect(btn['call'])
            if btn.has_key('singal'):
                btn['singal'].connect(btn['enCall'])
                btn['enCall']()

    def load_tableviews(self, tableviews, db):
        for tableview in tableviews:
            if tableview.has_key('showGrid'):
                tableview['widget'].setShowGrid(tableview['showGrid'])
            tableview['widget'].setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选中的方式
            model = qtmodel(tableview['model'], db, tableview['widget'])
            if tableview.has_key('menu'):
                menu = qtMenu(tableview['menu'], tableview['name'], tableview['widget'])
            if tableview.has_key('doubleClick'):
                tableview['widget'].doubleClicked.connect(tableview['doubleClick'])
            if tableview.has_key('clicked'):
                tableview['widget'].clicked.connect(tableview['clicked'])
            model.load()

    def load_treeviews(self, treeviews, db):
        for treeview in treeviews:
            model = qtTreeModel(treeview['model'], db, [["id", ">", 0]], treeview['widget'])
            treeview['widget'].setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选中的方式
            if treeview.has_key('menu'):
                menu = qtMenu(treeview['menu'], treeview['name'], treeview['widget'])
            if treeview.has_key('doubleClick'):
                treeview['widget'].doubleClicked.connect(treeview['doubleClick'])
            if treeview.has_key('clicked'):
                treeview['widget'].clicked.connect(treeview['clicked'])

    def loadCheckboxs(self, checkBoxs):
        for checkbox in checkBoxs:
            box = checkbox['widget']
            box.setTristate(False)
            val = checkbox['init']()
            box.setCheckState(val)
            box.stateChanged.connect(checkbox['save'])
