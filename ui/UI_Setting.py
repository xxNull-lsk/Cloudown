#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTaskActive import *
from ui.WidgetTaskWaiting import UITaskWaiting
from ui.WidgetTaskStopped import UITaskStopped


class SystemSettings:
    SERVER_URL = 'http://118.25.17.65:6800/jsonrpc'
    SERVER_TOKEN = 'allan'
    REFRESH = 1


class UiSetting(QDialog):
    settings = SystemSettings()

    def __init__(self, parent):
        super(UiSetting, self).__init__(parent)
        self.setObjectName('UiSetting')
        self.resize(800, 600)
        
        self.setWindowTitle("配置")

        self.main_layout = QGridLayout(self)     # 窗口的整体布局
        self.main_layout.setContentsMargins(60, 60, 20, 20)
        label_url = QLabel("服务器URL：")
        label_url.setFixedHeight(28)
        self.main_layout.addWidget(label_url, 0, 0)
        edit_url = QTextEdit(self.settings.SERVER_URL)
        edit_url.setFixedHeight(28)
        self.main_layout.addWidget(edit_url, 0, 1, 1, 3)

        label_token = QLabel("服务器token：")
        label_token.setFixedHeight(28)
        self.main_layout.addWidget(label_token, 1, 0)
        edit_token = QTextEdit(self.settings.SERVER_TOKEN)
        edit_token.setFixedHeight(28)
        self.main_layout.addWidget(edit_token, 1, 1, 1, 2)

        label_refresh = QLabel("刷新频率：")
        label_refresh.setFixedHeight(28)
        self.main_layout.addWidget(label_refresh, 2, 0)
        spin_refresh = QSpinBox()
        spin_refresh.setFixedHeight(28)
        spin_refresh.setMinimum(1)
        spin_refresh.setMaximum(60)
        spin_refresh.setValue(self.settings.REFRESH)
        self.main_layout.addWidget(spin_refresh, 2, 1)

        self.setWindowModality(Qt.ApplicationModal)
