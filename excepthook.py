# coding=utf-8
import os
import platform
import sys
import threading
import time
import traceback

from PyQt4 import QtGui

from guiqt import ui_compile
from version_master import appversion

Max_Traceback_List_Size = 20

ui_compile('excepthook')

from uiexcepthook import Ui_Dialog


class execptDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, tip, msg, list, *args):
        try:
            QtGui.QDialog.__init__(self, *args)
            self.setupUi(self)
            self.textBrowser.setText(msg + tip )
            for line in list:
                self.textBrowser.append(line)
            self.exec_()
        except Exception, ex:
            print ex.message


def Display_Exception_Dialog(e_type, e_value, e_tb, bug_report_path):
    trcbck_lst = []
    for i, line in enumerate(traceback.extract_tb(e_tb)):
        trcbck = " " + str(i + 1) + ". "
        if line[0].find(os.getcwd()) == -1:
            trcbck += "file : " + str(line[0]) + ",   "
        else:
            trcbck += "file : " + str(line[0][len(os.getcwd()):]) + ",   "
        trcbck += "line : " + str(line[1]) + ",   " + "function : " + str(line[2])
        trcbck_lst.append(trcbck)

        # Allow clicking....
    #    cap = wx.Window_GetCapture()
    #    if cap:
    #        cap.ReleaseMouse()

    dlg = execptDialog(
        (u"""
程序发生错误. 信息已保存到 :
(%s)

你需要重新启动程序.

Traceback:
""") % bug_report_path +
        repr(e_type) + " : " + repr(e_value),
        "Error",
        trcbck_lst)

    return dlg


def get_last_traceback(tb):
    while tb.tb_next:
        tb = tb.tb_next
    return tb


def format_namespace(d, indent='    '):
    return '\n'.join(['%s%s: %s' % (indent, k, repr(v)[:10000]) for k, v in d.iteritems()])


ignored_exceptions = []  # a problem with a line in a module is only reported once per session


def AddExceptHook(path, app_version='[No version]'):  # , ignored_exceptions=[]):

    def handle_exception(e_type, e_value, e_traceback):
        traceback.print_exception(e_type, e_value,
                                  e_traceback)  # this is very helpful when there's an exception in the rest of this func
        last_tb = get_last_traceback(e_traceback)
        ex = (last_tb.tb_frame.f_code.co_filename, last_tb.tb_frame.f_lineno)
        if ex not in ignored_exceptions:
            date = time.ctime()
            bug_report_path = path + os.sep + "bug_report_" + date.replace(':', '-').replace(' ', '_') + ".txt"
            ignored_exceptions.append(ex)
            info = {
                # 'app-title' : wx.GetApp().GetAppName(), # app_title
                'app-version': appversion,
                # 'wx-version' : wx.VERSION_STRING,
                #  'wx-platform' : wx.Platform,
                'python-version': platform.python_version(),  # sys.version.split()[0],
                'platform': platform.platform(),
                'e-type': e_type,
                'e-value': e_value,
                'date': date,
                'cwd': os.getcwd(),
            }
            if e_traceback:
                info['traceback'] = ''.join(traceback.format_tb(e_traceback)) + '%s: %s' % (e_type, e_value)
                last_tb = get_last_traceback(e_traceback)
                exception_locals = last_tb.tb_frame.f_locals  # the locals at the level of the stack trace where the exception actually occurred
                info['locals'] = format_namespace(exception_locals)
                if 'self' in exception_locals:
                    try:
                        info['self'] = format_namespace(exception_locals['self'].__dict__)
                    except:
                        pass

            output = open(bug_report_path, 'w')
            lst = info.keys()
            lst.sort()
            for a in lst:
                output.write(a + ":\n" + str(info[a]) + "\n\n")
            Display_Exception_Dialog(e_type, e_value, e_traceback, bug_report_path)

    # sys.excepthook = lambda *args: wx.CallAfter(handle_exception, *args)
    sys.excepthook = handle_exception

    init_old = threading.Thread.__init__

    def init(self, *args, **kwargs):
        init_old(self, *args, **kwargs)
        run_old = self.run

        def run_with_except_hook(*args, **kw):
            try:
                run_old(*args, **kw)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init

    def test_except():
        handle_exception('', '', '')
