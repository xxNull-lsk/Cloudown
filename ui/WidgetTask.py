#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Misc import *
import os
import gl


class UITask(QWidget):
    def __init__(self, qss):
        super(UITask, self).__init__()
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

        self.button_filename = QLabel()
        # self.button_filename.clicked.connect(self._command)
        self.top_layout.addWidget(self.button_filename, 0, 0, 1, 3)

        self.commands = QHBoxLayout()
        self.commands.setAlignment(Qt.AlignRight)
        self.commands.setSpacing(2)
        self.top_layout.addLayout(self.commands, 0, 3, 1, 1)

        self.command_open = QPushButton()
        self.command_open.setFixedWidth(32)
        pm = QPixmap('./icons/open.png')
        self.command_open.setIcon(QIcon(pm))
        with open('./qss/command_button.qss', 'r') as f:
            self.command_open.setStyleSheet(f.read())
        self.command_open.setToolTip("打开文件所在目录")
        self.command_open.clicked.connect(self._command)
        self.commands.addWidget(self.command_open)

        self.command_delete = QPushButton()
        self.command_delete.setFixedWidth(32)
        pm = QPixmap('./icons/delete.png')
        self.command_delete.setIcon(QIcon(pm))
        with open('./qss/command_button.qss', 'r') as f:
            self.command_delete.setStyleSheet(f.read())
        self.command_delete.setToolTip("删除文件")
        self.command_delete.clicked.connect(self._command)
        self.commands.addWidget(self.command_delete)

        self.command_details = QPushButton()
        self.command_details.setFixedWidth(32)
        pm = QPixmap('./icons/details.png')
        self.command_details.setIcon(QIcon(pm))
        with open('./qss/command_button.qss', 'r') as f:
            self.command_details.setStyleSheet(f.read())
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

    def setData(self, task):
        self.task = task
        self.label_file_size.setText(size2string(task['totalLength']))
        self.label_upload_size.setText(size2string(task['uploadLength']))

        file_name = ""
        if "bittorrent" in task and 'info' in task["bittorrent"]:
            file_name = task["bittorrent"]["info"]['name']
        if file_name is "" and len(task["files"]) > 0:
            file_name = task["files"][0]["path"]

        font_metrics = QFontMetrics(self.font())
        self.button_filename.setToolTip(file_name)
        file_name = os.path.split(file_name)[1]
        if font_metrics.width(file_name) > self.button_filename.width():
            file_name = font_metrics.elidedText(file_name, Qt.ElideRight, self.button_filename.width())
        self.button_filename.setText(file_name)

    def _command(self):
        sender = self.sender()
        if (sender is self.command_details) or (sender is self.button_filename):
            dm = gl.get_value('dm')
            dm.main_wnd.ui_details.set_data(self.task)
        elif sender is self.command_open:
            file_name = ""
            if "bittorrent" in self.task and 'info' in self.task["bittorrent"]:
                file_name = self.task["bittorrent"]["info"]['name']
            if file_name is "" and len(self.task["files"]) > 0:
                file_name = self.task["files"][0]["path"]
            try:
                os.startfile(os.path.join(self.task['dir'], file_name))
            except FileNotFoundError as err:
                print(err)
        elif sender is self.command_delete:
            if QMessageBox.question(self, "询问", "确认要删除该任务？", QMessageBox.Ok | QMessageBox.No) == QMessageBox.No:
                return
            aria2 = gl.get_value('aria2')
            if self.task["status"] in ('active', 'waiting', 'paused'):
                aria2.remove(self.task['gid'])
                aria2.remove_stoped(self.task['gid'])
            else:
                aria2.remove_stoped(self.task['gid'])
