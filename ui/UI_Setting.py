#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import json


class SystemSettings:
    values = {
        'SERVER_URL': 'http://118.25.17.65:6800/jsonrpc',
        'SERVER_TOKEN': 'allan',
        'REFRESH': 1
    }
    file = None

    def load(self, file_name):
        self.file = file_name
        if os.path.exists(file_name):
            self.values = json.loads(open(file_name, 'rb').read())

    def save(self, file_name):
        self.file = file_name
        open(file_name, 'w+b').write(json.dumps(self.values, indent=4))

    def writeback(self):
        if self.file is not None:
            open(self.file, 'w+b').write(json.dumps(self.values, indent=4))


class UiSetting(QDialog):
    settings = SystemSettings()

    def __init__(self, parent):
        super(UiSetting, self).__init__(parent)
        self.setObjectName('UiSetting')
        self.resize(800, 600)
        
        self.setWindowTitle("配置")
        self.settings.load("setting.json")

        self.main_layout = QGridLayout(self)     # 窗口的整体布局
        self.main_layout.setContentsMargins(60, 60, 20, 20)
        label_url = QLabel("服务器URL：")
        label_url.setFixedHeight(28)
        self.main_layout.addWidget(label_url, 0, 0)
        self.edit_url = QTextEdit(self.settings.values['SERVER_URL'])
        self.edit_url.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_url, 0, 1, 1, 4)

        label_token = QLabel("服务器token：")
        label_token.setFixedHeight(28)
        self.main_layout.addWidget(label_token, 1, 0)
        self.edit_token = QTextEdit(self.settings.values['SERVER_TOKEN'])
        self.edit_token.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_token, 1, 1, 1, 2)

        label_refresh = QLabel("刷新频率：")
        label_refresh.setFixedHeight(28)
        self.main_layout.addWidget(label_refresh, 2, 0)
        self.spin_refresh = QSpinBox()
        self.spin_refresh.setFixedHeight(28)
        self.spin_refresh.setMinimum(1)
        self.spin_refresh.setMaximum(60)
        self.spin_refresh.setValue(self.settings.values['REFRESH'])
        self.main_layout.addWidget(self.spin_refresh, 2, 1)

        self.button_ok = QPushButton("确定")
        self.button_ok.setFixedHeight(32)
        self.button_ok.clicked.connect(self.on_ok)
        self.main_layout.addWidget(self.button_ok, 4, 1)

        button_cancel = QPushButton("取消")
        button_cancel.setFixedHeight(32)
        button_cancel.clicked.connect(self.close)
        self.main_layout.addWidget(button_cancel, 4, 3)

        self.setWindowModality(Qt.ApplicationModal)

    def on_ok(self):
        self.settings.values["REFRESH"] = self.spin_refresh.value()
        self.settings.values["SERVER_TOKEN"] = self.edit_token.toPlainText()
        self.settings.values["SERVER_URL"] = self.edit_url.toPlainText()
        self.settings.writeback()
