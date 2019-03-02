#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Misc import *
import os


class UITask(QWidget):
    def __init__(self, qss):
        super(UITask, self).__init__()
        self.setObjectName('TaskStopped')
        self.task = None
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        if os.path.exists(qss):
            self.list_style = open(qss, 'r').read()  # 导入qss样式

        self.layout = QGridLayout(self)     # 窗口的整体布局
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.button_filename = QCommandLinkButton()
        self.button_filename.clicked.connect(self._command)
        self.layout.addWidget(self.button_filename, 0, 0, 3, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.commands = QHBoxLayout()
        # self.commands.setContentsMargins(5, 5, 5, 5)
        self.commands.setSpacing(2)

        self.command_open = QPushButton("打开")
        self.command_open.setToolTip("打开文件所在目录")
        self.command_open.clicked.connect(self._command)
        self.commands.addWidget(self.command_open)

        self.command_delete = QPushButton("删除")
        self.command_delete.setToolTip("删除文件")
        self.command_delete.clicked.connect(self._command)
        self.commands.addWidget(self.command_delete)

        self.command_details = QPushButton("详情")
        self.command_details.setToolTip("查看详情")
        self.command_details.clicked.connect(self._command)
        self.commands.addWidget(self.command_details)

        self.layout.addLayout(self.commands, 0, 3, 2, 2, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.label_file_size = QLabel()
        self.label_file_size.setToolTip("文件大小")
        self.layout.addWidget(self.label_file_size, 2, 0, 1, 2)

        self.label_upload_size = QLabel()
        self.label_upload_size.setToolTip("上传大小")
        self.layout.addWidget(self.label_upload_size, 2, 2)

    def setData(self, task):
        self.task = task
        self.label_file_size.setText(size2string(task['totalLength']))
        self.label_upload_size.setText(size2string(task['uploadLength']))

        file_name = ""
        if "bittorrent" in task and 'info' in task["bittorrent"]:
            file_name = task["bittorrent"]["info"]['name']
        if file_name is "" and len(task["files"]) > 0:
            file_name = task["files"][0]["path"]
        self.button_filename.setText(file_name)

    def _command(self):
        print("_command{}".format(self))
        sender = self.sender()
        if (sender is self.command_details) or (sender is self.button_filename):
            # TODO: 查看详情
            QMessageBox.information(self, "TODO", "查看详情", QMessageBox.Ok)
            pass
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
            # TODO: 删除文件及任务
            QMessageBox.information(self, "TODO", "删除文件及任务", QMessageBox.Ok)
            pass
