#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Misc import *
import os
import sys
import gl
import _thread
import logging
import time


class UiCommandButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0)
        self.animation = None
        self._opacity = 0.0

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.setWindowOpacity(val)

    def setWindowOpacity(self, level: float):
        super().setWindowOpacity(level)
        op = QGraphicsOpacityEffect()
        op.setOpacity(level)
        self.setGraphicsEffect(op)

    def animation_show(self):
        if self.animation is not None:
            self.animation.stop()
        self.animation = QPropertyAnimation(self, b'opacity')
        self.animation.setDuration(500)
        self.animation.setStartValue(self.opacity)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InCirc)
        self.animation.start()

    def animation_hide(self):
        if self.animation is not None:
            self.animation.stop()
        self.animation = QPropertyAnimation(self, b'opacity')
        self.animation.setDuration(500)
        self.animation.setStartValue(self.opacity)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.OutCirc)
        self.animation.start()


class UITask(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('TaskStopped')
        self.setMinimumWidth(160)
        self.task = None
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.top_layout = QGridLayout()
        self.layout.addLayout(self.top_layout)

        self.label_filename = QLabel()
        self.label_filename.setMinimumWidth(240)
        self.top_layout.addWidget(self.label_filename, 0, 0, 1, 5)

        self.commands = QHBoxLayout()
        self.commands.setAlignment(Qt.AlignRight)
        self.commands.setSpacing(2)
        self.top_layout.addLayout(self.commands, 0, 6)

        self.command_open = UiCommandButton()
        self.command_open.setObjectName("CommandOpenFolder")
        self.command_open.setToolTip(self.tr('Open folder of the file'))
        self.command_open.clicked.connect(self._command)
        self.commands.addWidget(self.command_open)

        self.command_delete = UiCommandButton()
        self.command_delete.setObjectName('CommandDeleteTask')
        self.command_delete.setToolTip(self.tr("Delete"))
        self.command_delete.clicked.connect(self._command)
        self.commands.addWidget(self.command_delete)

        self.command_details = UiCommandButton()
        self.command_details.setObjectName('CommandDetails')
        self.command_details.setToolTip(self.tr("Details"))
        self.command_details.clicked.connect(self._command)
        self.commands.addWidget(self.command_details)

        self.info_layout = QHBoxLayout()
        self.layout.addLayout(self.info_layout)

        self.label_file_size = QLabel()
        self.label_file_size.setFixedWidth(180)
        self.label_file_size.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_file_size.setToolTip(self.tr("File size"))
        self.info_layout.addWidget(self.label_file_size)

        self.label_upload_size = QLabel()
        self.label_upload_size.setFixedWidth(90)
        self.label_upload_size.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_upload_size.setToolTip(self.tr("Upload size"))
        self.info_layout.addWidget(self.label_upload_size)
        self.info_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.command_open.animation_show()
        self.command_delete.animation_show()
        self.command_details.animation_show()

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.command_open.animation_hide()
        self.command_delete.animation_hide()
        self.command_details.animation_hide()

    @staticmethod
    def get_task_name(task):
        file_name = ''
        if "bittorrent" in task and 'info' in task["bittorrent"]:
            file_name = task["bittorrent"]["info"]['name']
        if file_name == "" and len(task["files"]) > 0:
            file_name = task["files"][0]["path"]
            if file_name == '' and len(task["files"][0]['uris']) > 0:
                file_name = task["files"][0]['uris'][0]['uri']
        return file_name

    def set_task(self, task):
        self.task = task
        self.label_file_size.setText('{0}'.format(size2string(task['totalLength'])))
        if task['uploadLength'] != '0':
            upload_length = size2string(task['uploadLength'])
        else:
            upload_length = ''
        self.label_upload_size.setText('{0:>25}'.format(upload_length))

        file_name = self.get_task_name(task)

        font_metrics = QFontMetrics(self.font())
        self.label_filename.setToolTip(file_name)
        file_name = os.path.split(file_name)[1]
        if font_metrics.width(file_name) > self.label_filename.width():
            file_name = font_metrics.elidedText(file_name, Qt.ElideRight, self.label_filename.width())
        self.label_filename.setText(file_name)

    @staticmethod
    def thread_delete_file(path):
        logging.info('deleting {0}'.format(path))
        if not os.path.exists(path):
            logging.error('not exist {0}'.format(path))

        try:
            rm_dir(path)
            logging.info('deleting {0} successed'.format(path))
        except Exception as err:
            logging.error('delete {0} failed!{1}'.format(path, err))

    def _command(self):
        sender = self.sender()
        dm = gl.get_value('dm')
        if (sender is self.command_details) or (sender is self.label_filename):
            dm.main_wnd.show_details(self.task)
        elif sender is self.command_open:
            if not dm.settings.values['IS_LOCALE']:
                UiMessageBox.warning(self,
                                     self.tr('Warn'),
                                     self.tr("Can't open folder when in remote mode"),
                                     QMessageBox.Ok)
                return
            file_name = self.get_task_name(self.task)
            try:
                path = os.path.join(self.task['dir'], file_name)
                path = os.path.abspath(path)
                if sys.platform == 'windows':
                    os.system('explorer /e,/select,{}'.format(path))
                elif sys.platform == 'linux':
                    os.system('open {}'.format(path))
                elif sys.platform == 'darwin':
                    os.system('open {}'.format(path))
            except FileNotFoundError as err:
                print(err)
        elif sender is self.command_delete:
            ret = UiMessageBox.warning(self,
                                       self.tr('Warn'),
                                       self.tr("Are you sure to delete this task?"),
                                       QMessageBox.Ok | QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                return
            is_detect_file = False
            if dm.settings.values['IS_LOCALE']:
                file_name = self.get_task_name(self.task)
                path = os.path.join(self.task['dir'], file_name)
                path = os.path.abspath(path)
                if os.path.exists(path) and \
                        UiMessageBox.question(self,
                                              self.tr('Question'),
                                              self.tr('Are you sure to delete file{} of this task?').format(path),
                                              QMessageBox.Ok | QMessageBox.Cancel) == QMessageBox.Ok:
                    is_detect_file = True
            else:
                path = ''
            aria2 = gl.get_value('aria2')
            if self.task["status"] in ('active', 'waiting', 'paused'):
                aria2.remove(self.task['gid'])

                while True:
                    try:
                        ret = aria2.get_status(self.task['gid'])
                    except:
                        break
                    if ret['result']['status'] == 'removed':
                        break
                    time.sleep(0.5)

            aria2.remove_stoped(self.task['gid'])
            if is_detect_file:
                _thread.start_new_thread(self.thread_delete_file, (path, ))
        aria2 = gl.get_value('aria2')
        aria2.save_session()

    def tr(self, sourceText, disambiguation=None, n=-1):
        trans = gl.get_value('language')
        ret = trans.translate('UITaskActive', sourceText, disambiguation, n)
        if ret is not None and ret != '':
            return ret
        ret = trans.translate('UITaskStopped', sourceText, disambiguation, n)
        if ret is not None and ret != '':
            return ret
        ret = trans.translate('UITaskWaiting', sourceText, disambiguation, n)
        if ret is not None and ret != '':
            return ret
        ret = trans.translate('UITask', sourceText, disambiguation, n)
        if ret is not None and ret != '':
            return ret
        return super().tr(sourceText, disambiguation, n)
