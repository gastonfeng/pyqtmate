# coding=utf-8

import time

import odoorpc as odoorpc


class odoopeek(object):
    def __init__(self):
        self.singal = False

    def version(self):
        return self.odoo.version

    def setSingal(self, s):
        self.singal = s

    def login(self, url, port, db, username, password):
        try:
            self.odoo = odoorpc.ODOO(url, 'jsonrpc', port)
            self.odoo.login(db, username, password)
        except Exception, e:
            print e.message
            return False
        return True

    def recordCount(self, table, filter=[]):
        try:
            module = self.odoo.env[table]
            kw = module.search_count(filter)
        except  Exception, e:
            print e.message
            kw = False
        return kw

    def read(self, table, ids):
        try:
            module = self.odoo.env[table]
            kw = module.read(ids)
        except Exception, e:
            kw = False
        # self.mutex.release()
        return kw

    def write(self, table, ids, values):
        try:
            module = self.odoo.env[table]
            kw = module.write(ids, values)
            if self.singal:
                self.singal.emit({'db': table}, False)
        except Exception, e:
            print e.message
            kw = False
        # self.mutex.release()
        return kw

    def search(self, table, filter, limit=25, offset=0, order=''):
        try:
            module = self.odoo.env[table]
            ids = self.odoo.execute_kw(table, 'search', [filter], {'limit': limit, 'offset': offset, 'order': order})
        except Exception, e:
            print e.message
            ids = False
        return ids

    def search_write(self, table, filter, values):
        try:
            module = self.odoo.env[table]
            ids = module.search(filter)
            kw = module.write(ids, values)
            if self.singal:
                self.singal.emit({'db': table}, False)
        except Exception, e:
            print e
            kw = False
        # self.mutex.release()
        return kw

    def search_read(self, table, filter, limit=25, offset=0, order=''):
        try:
            module = self.odoo.env[table]
            ids = self.odoo.execute_kw(table, 'search', [filter], {'limit': limit, 'offset': offset, 'order': order})
            return module.read(ids)
        except Exception, e:
            print e.message
            kw = False
        return kw

    def browse(self, table, ids):
        try:
            if table in self.odoo.env:
                module = self.odoo.env[table]
                return module.browse(ids)
        except Exception, ex:
            print ex.message
        return False

    def search_browse(self, table, filter, limit=25, offset=0, order=''):
        try:
            if table in self.odoo.env:
                module = self.odoo.env[table]
                ids = module.search(filter, limit=limit, offset=offset, order=order)
                return module.browse(ids)
        except Exception, e:
            print e.message
        return False

    def create(self, table, vals):
        try:
            module = self.odoo.env[table]
            ids = module.create(vals)
            context = module.read(ids)
            if self.singal:
                self.singal.emit({'db': table}, False)
        except Exception, e:
            print e.message
            context = False
        return context

    def unlink(self, table, ids):
        try:
            module = self.odoo.env[table]
            kw = module.unlink(ids)
            if self.singal:
                self.singal.emit({'db': table}, False)
        except Exception, e:
            print e.message
            kw = False
        return kw

    def search_unlink(self, table, filter):
        try:
            module = self.odoo.env[table]
            ids = module.search(filter)
            kw = module.unlink(ids)
            if self.singal:
                self.singal.emit({'db': table}, False)
        except Exception, e:
            print e.message
            kw = False
        return kw

    def mirgateModule(self, module, ver):
        urls = 'http://www.lichousheng.cn/odooapps/IMConnecter.zip'
        mdl = self.odoo.env['ir.module.module']
        context = mdl.search_read([('name', '=', module)])
        if not context or context[0][u'latest_version'] != ver:
            mdl.install_from_urls({module: urls})
            time.sleep(10)
            # mdl.button_immediate_upgrade(context[0]['id'])


