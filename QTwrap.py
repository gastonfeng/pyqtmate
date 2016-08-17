# coding=utf-8
import os
import re
from datetime import datetime
from xml.dom import minidom

import PyQt4
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import QCursor, QPushButton, QLabel, QPixmap, QIcon, QImage, QColor, qRgb

from pushbutton import qpushbutton
from xml_misc import isxml, getXML

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
    # for i, line in enumerate(lines):
    # lines[i] = '<li>' + line + '</li>'
    # lines[i] = '<p>' + line + '</p>'
    html = ''.join(lines)
    pics = re.findall(pic_pattern, html)
    for pic in pics:
        filename = re.findall(file_pattern, pic)[0]
        p = QPixmap('image/' + filename)
        w = p.width()
        if w > 400:
            w = 400
        pic_new = unicode('<img src="file:///%s/image/' % os.getcwd() + filename + '" width=%d >' % w)
        html = re.sub(pic_pattern, pic_new, html)  # 替换
    faces = re.findall(face_pattern, html)
    for face in faces:
        filename = re.findall(face_file_pattern, face)[0]
        '''@addgroup QwebView :本地图片需要使用绝对路径才能显示,或通过资源方式调用'''
        pic_new = '<img src="file:///%s/image/' % os.getcwd() + filename + '">'
        html = re.sub(face_pattern, pic_new, html)
    return html


class menuAction(QtGui.QAction):
    '''菜单项封装接口类
    pmenu:所属菜单的名称
    '''

    def __init__(self, parent, name, pmenu, call):
        QtGui.QAction.__init__(self, name, parent)
        self.pmenu = pmenu
        self.triggered.connect(call)


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
                        sitem = menuAction(self, s['name'], self.symbol, m['slot'])
                        if s.has_key('id'):
                            sitem.setData(s['id'])
                        item.addAction(sitem)
                else:
                    item = menuAction(self, m['name'], self.symbol, m['slot'])
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


def widget_qq_xml(parent, txt):
    ctl = QtGui.QLabel(parent)
    ctl.setWordWrap(True)
    xml = minidom.parseString(txt.encode('utf-8'))
    msg = xml.documentElement
    # msg = root.getElementsByTagName('msg')[0]
    serviceID = msg.getAttribute('serviceID')
    templateID = msg.getAttribute('templateID')
    brief = msg.getAttribute('brief')
    sourcePublicUin = msg.getAttribute('sourcePublicUin')
    sourceMsgId = msg.getAttribute('sourceMsgId')
    url = msg.getAttribute('url')
    flag = msg.getAttribute('flag')
    sType = msg.getAttribute('sType')
    adverSign = msg.getAttribute('adverSign')
    adverKey = msg.getAttribute('adverKey')
    action = msg.getAttribute('action')
    item = msg.getElementsByTagName('item')[0]
    layout = item.getAttribute('layout')
    picture = item.getElementsByTagName('picture')[0]
    cover = picture.getAttribute('cover')
    w = picture.getAttribute('w')
    h = picture.getAttribute('h')
    title = item.getElementsByTagName('title')[0]
    for node in title.childNodes:
        if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            title_txt = node.data
    summary = item.getElementsByTagName('summary')[0]
    for node in summary.childNodes:
        if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            summary_txt = node.data
    # source = msg.getElementsByTagName('source')[0]
    # name = source.getAttribute('name')
    # icon = source.getAttribute('icon')
    # action = source.getAttribute('action')
    # a_actionData = source.getAttribute('a_actionData')
    # i_actionData = source.getAttribute('i_actionData')
    # appid = source.getAttribute('appid')
    ctl.setText(brief)
    return ctl


def widgetQqmsg(parent, record):
    fontname = record['fontname']
    fontsize = record['fontsize']
    rgba = int(record['color'])
    color = QtGui.QColor()
    color.setRgba(rgba)
    txt = record['subject']
    ctl = QtGui.QLabel(parent)
    ctl.setWordWrap(True)
    if isxml(txt):
        xml, txt = getXML(txt)
        widget_qq_xml(ctl, xml)
    html = qqmsg2html(txt)
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


def img_merage(img1, img2):
    '''两个图片文件叠加,返回QPixmap'''
    scale = 0.5
    pm1 = QImage(img1)
    if pm1.isNull():
        raise
    pm2 = QImage(img2)
    if pm2.isNull():
        raise
    pm2 = pm2.scaled(pm1.width() * scale, pm1.height() * scale)
    for x in range(0, pm2.width()):
        for y in range(0, pm2.height()):
            oldColor = pm2.pixel(x, y)
            pm1.setPixel(x + pm1.width() - pm2.width(), y + pm1.height() - pm2.height(), oldColor)
    return QPixmap(pm1)


def greyScale(img):
    '''从图片文件转换灰度图片,返回QPixmap'''
    origin = QImage(img)
    newImage = QImage(origin.width(), origin.height(), QImage.Format_ARGB32)
    oldColor = QColor()
    for x in range(0, origin.width()):
        for y in range(0, origin.height()):
            oldColor = QColor(origin.pixel(x, y))
            average = (oldColor.red() + oldColor.green() + oldColor.blue()) / 3
            newImage.setPixel(x, y, qRgb(average, average, average))
    return QPixmap(newImage)

# 图像显示效果,叠加图像,变灰等等
def iconEffect(icon, effect):
    if effect == 1:
        return greyScale(icon)
    elif effect == 0:
        return img_merage(icon, ':/icon/woniu')
    return icon


# 查找图标文件
def getIcon(param, effect=None):
    if not param:
        param = 'QQ'
    img = (os.getcwd() + u'/头像/' + param + '.jpg')
    if os.path.isfile(img):
        return iconEffect(img, effect=effect)
    return iconEffect(':/icon/' + param, effect=effect)



class qtmodel(QtGui.QStandardItemModel):
    def __init__(self, tml, db, view):
        QtGui.QStandardItemModel.__init__(self)
        self.view = view
        self.rowsPerpage = 25
        self.pages = 0
        self.page = 0
        self.tmpl = tml
        self.filter = []  # 过滤器
        if tml.has_key('filter'):
            self.filter = tml['filter']
        self.db = db
        self.context = []
        view.setModel(self)
        # self.load()
        self.dataChanged.connect(self.tdataChanged)
        self.editing = False
        self.loading = False
        self.datChange = False
        self.lasttime = datetime.now()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.tmr_reload)

    def load(self):
        self.loading = True
        # if len(filter) == 0:
        #    filter = self.tmpl['filter']
        self.table = self.db.odoo.env[self.tmpl['table']]
        self.rows = self.table.search_count(self.filter)
        self.pages = self.rows / self.rowsPerpage
        # del self.context[:]
        limit = self.rowsPerpage
        if self.tmpl.has_key('limit'):
            limit = self.tmpl['limit']
        order = ''
        if self.tmpl.has_key('order'):
            order = self.tmpl['order']
        ids = self.table.search(self.filter, limit=limit, offset=self.page * self.rowsPerpage, order=order)
        self.context = self.table.browse(ids)
        if self.tmpl.has_key('distinct') and self.context:
            self.context = self.tmpl['distinct'](self.context)
        self.fill()
        if self.tmpl.has_key('doChange'):
            self.tmpl['doChange']()
        self.loading = False

    def reload(self):
        # if not self.loading:
        #    self.load()
        # return
        if not self.timer.isActive():
            self.timer.start(1000)

    def tmr_reload(self):
        if self.editing:
            return
        self.load()

    def setFilter_load(self, filter):
        self.filter = filter
        self.load()

    def search(self, key):
        del self.context[:]
        self.page = 0
        kw = self.db.search(self.tmpl['table'], filter)
        if len(kw) > 0:
            self.context = self.db.read(self.tmpl['table'], kw)
        self.fill()

    # @param:row,行索引编号
    # @param:level ,层次编号
    def fill_row(self, row, fields, record, level=0, parent=None):
        col_index = 0
        itemFirst = None
        for col in fields:
            if col.has_key('field') == False:
                val = col['default']
            else:
                field = col['field']
                val = record[field]
            if col.has_key('getContext'):
                func = col['getContext']
                val = func(record)
            item = QtGui.QStandardItem()
            if col.has_key('flag'):
                if Qt.ItemIsUserCheckable in col['flag']:
                    item.setCheckable(True)
                    item.setTristate(False)
                    # 设置可编辑
                    flag = item.flags()
                    if Qt.ItemIsEditable not in col['flag']:
                        flag &= ~ Qt.ItemIsEditable
                        item.setFlags(flag)

                    def chkstate(b):
                        if b == True:
                            return 2
                        return 0

                    item.setCheckState(chkstate(val))
            if col.has_key('refence'):
                v = val
                if v:
                    v = v.mapped('name')
                item = QtGui.QStandardItem(unicode(v))
            if col.has_key('one2many'):
                if val:
                    item.setText(unicode(val[col['one2many']]))
            elif col.has_key('many2one'):
                if val:
                    item.setText(unicode(val['name']))
            else:
                if val:
                    item = QtGui.QStandardItem(unicode(val))
            # 插入图标
            if not itemFirst and col.has_key('img_field'):  # 只在第一列插入
                effect = None
                if col.has_key('effect_field'):
                    effect = record[col['effect_field']]
                ico = record.ico
                if not ico:
                    ico = 'QQ'
                else:
                    if not isinstance(ico, str):
                        raise
                ico = getIcon(ico, effect)  # todo :()      #图标名从ico字段读入
                icon = QIcon()
                icon.addPixmap(ico)
                item.setIcon(icon)
            # 插入ToolTip提示信息
            if col.has_key('toolTip'):
                prefix = ''
                if col.has_key('toolTip_prefix'):
                    prefix = col['toolTip_prefix']
                tip = col['toolTip']
                tip = record[tip]
                tip = unicode(tip)
                item.setToolTip(prefix + tip)

            ##
            if parent:
                if not itemFirst:
                    parent.insertRow(row, item)
                else:
                    itemFirst.insertColumn(col_index, [item, ])
            else:
                self.setItem(row, col_index, item)
            id = record['id']
            item.setData(id, Qt.UserRole + 1)
            item.setData(level, Qt.UserRole + 2)
            if itemFirst == None:
                itemFirst = item
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
        return itemFirst

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
                self.fill_row(row, self.tmpl['fields'], q)
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
            self.fill_row(row, self.tmpl['fields'], record)
        else:
            if self.tmpl['fields'][index.column()].has_key('refence'):
                val = self.db.search(self.tmpl['fields'][index.column()]['refence'], [["name", "=", val]])[0]
            self.db.write(self.tmpl['table'], [id, ], {field: val})
        self.submit()
        self.load()
        self.datChange = False

    def getSelectindex(self):
        smodel = self.view.selectionModel()
        indexs = smodel.selectedRows()
        return indexs

    def getSelectId(self):
        indexs = self.getSelectindex()
        ids = []
        for index in indexs:
            ids.append(self.getId(index))
        return ids

    def getId(self, index):
        id = self.data(index, Qt.UserRole + 1).toInt()[0]
        return id

    def selSet(self):
        '''返回选中的记录集'''
        ids = self.getSelectId()
        records = self.table.browse(ids)
        return records

    def setId(self, index, id):
        self.setData(index, id, Qt.UserRole + 1)

    def getRecord(self, index):
        id = self.data(index, Qt.UserRole + 1).toInt()[0]
        return self.context[id]

    def removeRecord(self, index):
        ids = []
        if isinstance(index, list):
            for i in index:
                id = self.getId(index)
                ids.append(id)
        else:
            id = self.getId(index)
            ids.append(id)
        if len(ids) > 0:
            self.db.unlink(self.tmpl['table'], ids)
        # for i in index:
        #            self.removeRow(i.row())
        self.submit()
        self.load()

    def removeSelect(self):
        self.db.unlink(self.tmpl['table'], self.getSelectId())
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
        qtmodel.__init__(self, tml, db, view)

    def loadsubnode(self, parent, context):
        tmpl = self.tmpl['children']
        for record in context:
            col_index = 0
            itemfirst = None
            for col in tmpl['fields']:
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

    def load(self):
        self.editing = True
        group = self.tmpl['parent']
        table = group['table']
        cats = self.db.search_browse(table, [])
        row = 0
        for u in cats:
            item = self.fill_row(row, group['field'], u)
            f = group['group_field']
            row += 1

            child = self.tmpl['children']
            id = u.id
            subs = self.db.search_browse(child['table'], [[f, '=', id]])
            if not subs:
                continue
            subrow = 0
            max = 25

            for c in subs:
                sub = self.tmpl['children']
                self.fill_row(subrow, sub['fields'], c, 1, item)
                subrow += 1
                if subrow >= 25:
                    break
        self.editing = False

    def getLevel(self, index):
        if len(index) > 0:
            index = index[0]
        id = self.data(index, Qt.UserRole + 2).toInt()[0]
        return id

    def selSet(self):
        '''返回选中的记录集'''
        indexs = self.getSelectindex()
        level = self.getLevel(indexs)
        id = self.getSelectId()
        if level == 0:
            group = self.tmpl['parent']
            table = group['table']
            cats = self.db.search_browse(table, id)
            return level, cats
        elif level == 1:
            child = self.tmpl['children']
            subs = self.db.search_browse(child['table'], [['id', 'in', id]])
            return level, subs


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
