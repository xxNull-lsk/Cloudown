#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Misc import *
import os
import gl
import _thread
import logging
import time


class UITask(QWidget):
    def __init__(self, qss):
        super().__init__()
        self.setObjectName('TaskStopped')
        self.setMinimumWidth(160)
        self.task = None
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        if os.path.exists(qss):
            self.list_style = open(qss, 'r').read()  # 导入qss样式

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 第一行
        self.top_layout = QGridLayout()
        self.layout.addLayout(self.top_layout)

        self.label_filename = QLabel()
        self.top_layout.addWidget(self.label_filename, 0, 0, 1, 3)

        self.commands = QHBoxLayout()
        self.commands.setAlignment(Qt.AlignRight)
        self.commands.setSpacing(2)
        self.top_layout.addLayout(self.commands, 0, 3, 1, 1)

        self.command_open = QPushButton()
        self.command_open.setObjectName("CommandOpenFolder")
        self.command_open.setToolTip("打开文件所在目录")
        self.command_open.clicked.connect(self._command)
        self.commands.addWidget(self.command_open)

        self.command_delete = QPushButton()
        self.command_delete.setObjectName('CommandDeleteTask')
        self.command_delete.setToolTip("删除文件")
        self.command_delete.clicked.connect(self._command)
        self.commands.addWidget(self.command_delete)

        self.command_details = QPushButton()
        self.command_details.setObjectName('CommandDetails')
        self.command_details.setToolTip("查看详情")
        self.command_details.clicked.connect(self._command)
        self.commands.addWidget(self.command_details)

        # 第二行
        self.info_layout = QHBoxLayout()
        self.layout.addLayout(self.info_layout)

        self.label_file_size = QLabel()
        self.label_file_size.setToolTip("文件大小")
        self.info_layout.addWidget(self.label_file_size)

        self.label_upload_size = QLabel()
        self.label_upload_size.setToolTip("上传大小")
        self.info_layout.addWidget(self.label_upload_size)

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
        self.label_file_size.setText(size2string(task['totalLength']))
        self.label_upload_size.setText(size2string(task['uploadLength']))

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
                QMessageBox.warning(self, '警告', '当前是远程服务器模式，无法打开文件所在目录。', QMessageBox.Ok)
                return
            file_name = self.get_task_name(self.task)
            try:
                path = os.path.join(self.task['dir'], file_name)
                path = os.path.abspath(path)
                print(path)
                os.system('explorer /e,/select,{}'.format(path))
            except FileNotFoundError as err:
                print(err)
        elif sender is self.command_delete:
            if QMessageBox.question(self, "警告", "确认要删除该任务？", QMessageBox.Ok | QMessageBox.No) == QMessageBox.No:
                return
            is_detect_file = False
            if dm.settings.values['IS_LOCALE']:
                file_name = self.get_task_name(self.task)
                path = os.path.join(self.task['dir'], file_name)
                path = os.path.abspath(path)
                if os.path.exists(path) and \
                        QMessageBox.question(self,
                                             "询问",
                                             "确认要删除该任务的文件（{}）吗？".format(path),
                                             QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
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
