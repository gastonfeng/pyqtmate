# coding=utf-8
import re
from datetime import datetime

import PyQt4
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import QAction, QCursor, QPushButton, QLabel, QPixmap, QIcon

from pushbutton import qpushbutton

pic_pattern = re.compile(r'\[image=\S+\.\w+\]')
file_pattern = re.compile(r'\[image=(\S+\.\w+)\]')
face_pattern = re.compile(r'\[face\d*\.\w+\]')
face_file_pattern = re.compile(r'\[face(\d*\.\w+)\]')


def qqmsg2html(msg):
    '''将txt以行为单位加上<li></li>标签'''

    def escape(txt):
        '''将txt文本中的空格、&、<、>、（"）、（'）转化成对应的的字符实体，以方便在html上显示'''
        txt = txt.replace('&', '&#38;')
        txt = txt.replace(' ', '&#160;')
        txt = txt.replace('<', '&#60;')
        txt = txt.replace('>', '&#62;')
        txt = txt.replace('"', '&#34;')
        txt = txt.replace('\'', '&#39;')
        return txt

    html = escape(msg)
    lines = html.split('\n')
    for i, line in enumerate(lines):
        lines[i] = '<li>' + line + '</li>'
        # lines[i] = '<p>' + line + '</p>'
    html = ''.join(lines)
    pics = re.findall(pic_pattern, html)
    for pic in pics:
        filename = re.findall(file_pattern, pic)[0]
        pic_new = unicode('<img src="image/' + filename + '" >')
        html = re.sub(pic_pattern, pic_new, html)
    faces = re.findall(face_pattern, html)
    for face in faces:
        filename = re.findall(face_file_pattern, face)[0]
        pic_new = '<img src="image/' + filename + '">'
        html = re.sub(face_pattern, pic_new, html)
    return html


class qtMenu(QtGui.QMenu):
    def __init__(self, menulist, symbol, parent):
        QtGui.QMenu.__init__(self, parent)
        # self.setParent(view)
        self.list = menulist
        self.symbol = symbol
        parent.setContextMenuPolicy(Qt.CustomContextMenu)
        parent.customContextMenuRequested.connect(self.action)

    def fill(self):
        for m in self.list:
            if m.has_key('relayout'):
                m['relayout'](self)
            else:
                if m.has_key('submenu'):
                    item = self.addMenu(m['name'])
                    sub = m['submenu']
                    for s in sub:
                        sitem = QAction(s['name'], self)
                        sitem.triggered.connect(m['slot'])
                        if s.has_key('id'):
                            sitem.setData(s['id'])
                        item.addAction(sitem)
                else:
                    item = QAction(m['name'], self)
                    item.triggered.connect(m['slot'])
                    if m.has_key('id'):
                        item.setData(m['id'])
                    # item.triggered.connect()
                    self.addAction(item)
            if m.has_key('enable') and not m['enable']():
                item.setEnabled(False)
            else:
                item.setEnabled(True)


    def action(self, point):
        self.clear()
        self.fill()
        action = self.exec_(QCursor.pos())


def model_to_menu(model, action):
    menu = []
    for row in range(0, model.rowCount()):
        item = model.item(row, 0)
        text = item.text()
        if item.hasChildren():
            sub = []
            for child in range(0, item.rowCount()):
                sitem = item.child(child)
                sub.append({'name': sitem.text(), 'slot': action, 'id': item.data(Qt.UserRole + 1).toInt()[0]})
            menu.append({'name': text, 'slot': action, 'submenu': sub})
        else:
            menu.append({'name': text, 'slot': action, 'id': item.data(Qt.UserRole + 1).toInt()[0]})

    return menu


def widgetQqmsg(parent, record):
    fontname = record['fontname']
    fontsize = record['fontsize']
    rgba = int(record['color'])
    color = QtGui.QColor()
    color.setRgba(rgba)
    txt = record['subject']
    html = qqmsg2html(txt)
    ctl = QtGui.QLabel(parent)
    # ctl.setMinimumHeight(10)
    # ctl.setMaximumHeight(200)
    # ctl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum);
    # ctl.setWidgetResizable(True)
    font = QtGui.QFont()
    if fontname:
        font.setStyleName(fontname)
    if fontsize > 0:
        font.setPointSize(fontsize)
        ctl.setFont(font)
    pal = QtGui.QPalette()
    if rgba:
        pal.setColor(QtGui.QPalette.Text, color)
        ctl.setPalette(pal)
    ctl.setText(html)
    return ctl


class qtmodel(QtGui.QStandardItemModel):
    def __init__(self, tml, db, view):
        QtGui.QStandardItemModel.__init__(self)
        self.view = view
        self.rowsPerpage = 25
        self.pages = 0
        self.page = 0
        self.tmpl = tml
        self.db = db
        self.context = []
        view.setModel(self)
        self.load()
        self.dataChanged.connect(self.tdataChanged)
        self.editing = False
        self.datChange=False
        self.lasttime = datetime.now()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tmr_reload)

    def load(self, filter=[]):
        if len(filter) == 0:
            filter = self.tmpl['filter']
        self.rows = self.db.recordCount(self.tmpl['table'], filter)
        self.pages = self.rows / self.rowsPerpage
        # del self.context[:]
        limit = self.rowsPerpage
        if self.tmpl.has_key('limit'):
            limit = self.tmpl['limit']
        order=''
        if self.tmpl.has_key('order'):
            order=self.tmpl['order']
        self.context = self.db.search_read(self.tmpl['table'], filter,
                             limit=limit, offset=self.page * self.rowsPerpage,order=order)
        if self.tmpl.has_key('distinct') and self.context:
            self.context = self.tmpl['distinct'](self.context)
        self.fill()
        if self.tmpl.has_key('doChange'):
            self.tmpl['doChange']()

    def reload(self):
        #self.load()
        #return
        if not self.timer.isActive():
            self.timer.start(1000)

    def tmr_reload(self):
        if self.editing:
            return
        self.load()

    def search(self, key):
        kw = self.db.search(self.tmpl['table'], filter)
        del self.context[:]
        if len(kw) > 0:
            self.context = self.db.read(self.tmpl['table'], kw)
        self.fill()

    def fill_row(self, row, record):
        col_index = 0
        for col in self.tmpl['fields']:
            if col.has_key('field') == False:
                val = col['default']
            else:
                field = col['field']
                val = record[field]
                if col.has_key('getContext'):
                    val = col['getContext'](record)
            item = QtGui.QStandardItem()
            if Qt.ItemIsUserCheckable in col['flag']:
                item.setCheckable(True)
                item.setTristate(False)

                def chkstate(b):
                    if b == True:
                        return 2
                    return 0

                item.setCheckState(chkstate(val))
            elif col.has_key('refence'):
                v = val
                if v:
                    v = v[1]
                item = QtGui.QStandardItem(unicode(v))
            elif col.has_key('one2many'):
                if val:
                    item.setText(unicode(val[col['one2many']]))
            elif col.has_key('many2one'):
                if val:
                    item.setText(unicode(val[1]))
            else:
                if val:
                    item = QtGui.QStandardItem(unicode(val))
            # 设置可编辑
            flag = item.flags()
            if Qt.ItemIsEditable not in col['flag']:
                flag &= ~ Qt.ItemIsEditable
                item.setFlags(flag)
            self.setItem(row, col_index, item)
            id = record['id']
            item.setData(id, Qt.UserRole + 1)
            # id = item.data(Qt.UserRole + 1).toInt()
            # 设置嵌入控件
            if col.has_key('ctrl'):
                widget = col['ctrl']
                if widget['widget'] == 'button':
                    btn = QPushButton(col['name'], self.view)
                    btn.clicked.connect(widget['slot'])
                    index = self.index(row, col_index)
                    self.view.setIndexWidget(index, btn)
                elif widget['widget'] == 'button_close':
                    btn = qpushbutton('', self.view)
                    btn.setFlat(True)
                    pixmap = QPixmap('close.png')
                    pixmap = pixmap.scaled(QSize(16, 16))
                    icon = QIcon(pixmap)
                    btn.setIcon(icon)
                    btn.data = record
                    btn.clicked.connect(widget['slot'])
                    index = self.index(row, col_index)
                    self.view.setIndexWidget(index, btn)
                elif widget['widget'] == 'qq_face':
                    label = QLabel()
                    pixmap = val
                    img = pixmap.scaled(28, 28)
                    label.setPixmap(img)
                    index = self.index(row, col_index)
                    self.view.setIndexWidget(index, label)
                    item.setText('')
                elif widget['widget'] == 'qq_msg':
                    ctrl = widgetQqmsg(self.view, record)
                    index = self.index(row, col_index)
                    self.view.setIndexWidget(index, ctrl)
                    item.setText('')
                else:
                    raise
            col_index = col_index + 1

    def fill(self):
        self.editing = True
        self.clear()
        ColCount = len(self.tmpl['fields'])
        self.setColumnCount(ColCount)
        col_index = 0
        # 填充表头
        if self.tmpl.has_key('colHead') and self.tmpl['colHead']:
            for col in self.tmpl['fields']:
                self.setHeaderData(col_index, QtCore.Qt.Horizontal, col['name'])
                col_index = col_index + 1
        else:
            if isinstance(self.view, PyQt4.QtGui.QTableView):
                self.view.horizontalHeader().setVisible(False)
        row = 0
        if self.context:
            for q in self.context:
                self.fill_row(row, q)
                row = row + 1

        # 插入空行
        col_index = 0
        if self.tmpl.has_key('newLine') and self.tmpl['newLine'] == True:
            for col in self.tmpl['fields']:
                item = QtGui.QStandardItem("")
                self.setItem(row, col_index, item)
                col_index = col_index + 1
        if isinstance(self.view, QtGui.QTableView):
            """自动调整表格"""
            self.view.resizeColumnsToContents()
            self.view.resizeRowsToContents()
        self.editing = False

    def tdataChanged(self, index):
        if self.editing or self.datChange:
            return
        self.datChange = True
        item = self.data(index)
        row = index.row()
        total = self.rowCount()
        id = self.data(index, Qt.UserRole + 1).toInt()[0]
        field = self.tmpl['fields'][index.column()]
        if field.has_key('field'):
            field = field['field']
        else:
            self.datChange = False
            return
        if Qt.ItemIsUserCheckable in self.tmpl['fields'][index.column()]['flag']:
            if self.item(row, index.column()).checkState() == 0:
                val = False
            else:
                val = True
        else:
            val = unicode(item.toString())
        if id == 0:
            record = self.db.create(self.tmpl['table'], {field: val})
            self.fill_row(row, record)
        else:
            if self.tmpl['fields'][index.column()].has_key('refence'):
                val = self.db.search(self.tmpl['fields'][index.column()]['refence'], [["name", "=", val]])[0]
            self.db.write(self.tmpl['table'], [id, ], {field: val})
        self.submit()
        self.load()
        self.datChange = False

    def removeRecord(self, index):
        ids = []
        for i in index:
            id = self.data(i, Qt.UserRole + 1).toInt()[0]
            ids.append(id)
        if len(ids) > 0:
            self.db.unlink(self.tmpl['table'], ids)
        # for i in index:
        #            self.removeRow(i.row())
        self.submit()
        self.load()

    def updateRecord(self, index, col, field, value):
        ids = []
        for i in index:
            id = self.data(i, Qt.UserRole + 1).toInt()[0]
            if id == 0:
                continue
            ids.append(id)
            row = i.row()
            self.item(row, col).setText(value)
            # self.db.write(self.tmpl['table'],ids,field,value)


class qtTreeModel(qtmodel):
    def __init__(self, tml, db, filter, view):
        qtmodel.__init__(self, tml, db, filter, view)

    def loadnode(self, parent, pid, filter):
        if pid:
            p = self.db.search(self.tmpl['table'], [['parent_id', '=', pid]])
        else:
            p = self.db.search(self.tmpl['table'], filter)
        context = self.db.read(self.tmpl['table'], p)
        if not context:
            return
        for record in context:
            col_index = 0
            itemfirst = None
            for col in self.tmpl['fields']:
                if col.has_key('field'):
                    txt = unicode(record[col['field']])
                else:
                    txt = ''
                item = QtGui.QStandardItem(txt)
                if parent != None:
                    if itemfirst == None:
                        parent.appendRow(item)
                        itemfirst = item
                    else:
                        parent.setChild(itemfirst.index().row(), col_index, item)
                else:
                    if itemfirst == None:
                        self.appendRow(item)
                        itemfirst = item
                    else:
                        self.setItem(itemfirst.index().row(), col_index, item)
                item.setData(record['id'], Qt.UserRole + 1)
                col_index = col_index + 1
            self.loadnode(itemfirst, record['id'], [])

    def load(self, filter):
        self.loadnode(None, False, [["id", ">", 0]])


class qtComboboxmodel():
    def __init__(self, tml, db, combox):
        self.db = db
        self.tmpl = tml
        self.combox = combox
        self.items = self.load()
        self.combox.addItems(self.items)

    def load(self):
        kw = self.db.search(self.tmpl['table'], [['id', '>', 0]])
        context = self.db.read(self.tmpl['table'], kw)
        return ['%s' % x[self.tmpl['field']] for x in context]
