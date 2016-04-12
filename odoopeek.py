# coding=utf-8

import odoorpc as odoorpc


class odoopeek(object):
    def __init__(self, url, port):
        self.singal = False
        self.odoo = odoorpc.ODOO(url, 'jsonrpc', port)

    def version(self):
        return self.odoo.version

    def setSingal(self, s):
        self.singal = s

    def login(self, db, username, password):
        try:
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
                self.singal.emit({'db': table})
        except Exception, e:
            print e
            kw = False
        # self.mutex.release()
        return kw

    def search(self, table, filter, limit=25, offset=0, order=''):
        try:
            module = self.odoo.env[table]
            ids = self.odoo.execute_kw(table, 'search', [filter], {'limit': limit, 'offset': offset,'order':order})
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
                self.singal.emit({'db': table})
        except Exception, e:
            print e
            kw = False
        # self.mutex.release()
        return kw

    def search_read(self, table, filter, limit=25, offset=0, order=''):
        try:
            module = self.odoo.env[table]
            ids = self.odoo.execute_kw(table, 'search', [filter], {'limit': limit, 'offset': offset,'order':order})
            return module.read(ids)
        except Exception, e:
            print e.message
            kw = False
        return kw

    def search_browse(self, table, filter, limit=25, offset=0,order=''):
        try:
            if table in self.odoo.env:
                module = self.odoo.env[table]
                ids = module.search(filter, limit=limit, offset=offset,order=order)
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
                self.singal.emit({'db': table})
        except Exception, e:
            print e.message
            context = False
        return context

    def unlink(self, table, ids):
        try:
            module = self.odoo.env[table]
            kw = module.unlink(ids)
            if self.singal:
                self.singal.emit({'db': table})
        except Exception, e:
            print e.message
            kw = False
        return kw

    def search_unlink(self, table, filter):
        try:
            module = self.odoo.env[table]
            ids=module.search(filter)
            kw = module.unlink(ids)
            if self.singal:
                self.singal.emit({'db': table})
        except Exception, e:
            print e.message
            kw = False
        return kw

    def mirgateModule(self, module, ver):
        urls = 'http://www.woniu66.com/odooapps/IMConnecter.zip'
        mdl = self.odoo.env['ir.module.module']
        context = mdl.search_read([('name', '=', module)])
        if not context or context[0][u'latest_version'] != ver:
            mdl.install_from_urls({module: urls})


if __name__ == '__main__':
    odoo = odoopeek('localhost', '8888')
    print odoo.version()
    odoo.login('custormdb', 'IMCONNECT', '111111')
    odoo.create('kaikong.qq.buddy',
                                 ({'name': 'hello', 'qq': [(4,1)], 'buddy': str('qq')}))
    while True:
        ids = odoo.search('kaikong.qq.message', [('status', '=', 'new msg')])
        context = odoo.read('kaikong.qq.message', ids)
        ccc = odoo.search_read('kaikong.qq.message', [('status', '=', 'new msg')])
    # odoo.mirgateModule('IMConnecter', '8.0.0.2')

    mdl = odoo.odoo.env['module_config']
    # context=mdl.search_read([('name','=','modulemanager')])
    mdl.install_from_server()

    odoo.create('kaikong.qq.list', {'name': 'abcdef'})
    qq = odoo.recordCount('kaikong.qq.list')
    print qq
    qq = odoo.search('kaikong.qq.list', [])
    print qq
    qq = odoo.read('kaikong.qq.list', qq)
    print qq
