#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import gl
import json
import webbrowser


class UiAbout(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName('UiAbout')

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        dm = gl.get_value('dm')
        label_name = QLabel('{0} {1}'.format(dm.app_name, dm.app_version))
        label_name.setObjectName('application_name')
        main_layout.addWidget(label_name)
        btn_address = QCommandLinkButton(self.tr("Website ({0})").format(dm.app_url))
        btn_address.clicked.connect(self.on_open_website)
        main_layout.addWidget(btn_address)
        label_name = QLabel()
        main_layout.addWidget(label_name)

        aria_info = QVBoxLayout()
        main_layout.addLayout(aria_info)

        label_title = QLabel(self.tr('About Aria2'))
        aria_info.addWidget(label_title)

        self.label_version = QLabel()
        aria_info.addWidget(self.label_version)

        self.edit_feature = QTextEdit()
        self.edit_feature.setReadOnly(True)
        aria_info.addWidget(self.edit_feature)

        self._value_changed('aria2')

    def _value_changed(self, name):
        if name == 'aria2':
            aria2 = gl.get_value(name)
            if aria2 is None:
                return
            ret = aria2.get_version()
            self.label_version.setText(self.tr('Version: ') + ret['result']['version'])
            msg = self.tr('Features:') + '\n'
            for f in ret['result']['enabledFeatures']:
                msg = msg + '\t' + f + '\n'

            ret = aria2.list_methods()
            msg = msg + self.tr('Methods:') + '\n'
            for f in ret['result']:
                msg = msg + '\t' + f + '\n'

            self.edit_feature.setText(msg)

    def on_open_website(self):
        dm = gl.get_value('dm')
        webbrowser.open(dm.app_url)
