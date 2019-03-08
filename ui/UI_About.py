#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import gl
import json


class UiAbout(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName('UiAbout')

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        self.label_version = QLabel()
        main_layout.addWidget(self.label_version)

        self.label_feature = QLabel()
        main_layout.addWidget(self.label_feature)
        self._value_changed('aria2')

    def _value_changed(self, name):
        if name == 'aria2':
            aria2 = gl.get_value(name)
            if aria2 is None:
                return
            ret = aria2.get_version()
            self.label_version.setText('版本号：' + ret['result']['version'])
            msg = '特性：\n'
            for f in ret['result']['enabledFeatures']:
                msg = msg + '\t' + f + '\n'
            self.label_feature.setText(msg)
            #self.label_feature.setText(json.dumps(ret, indent=4))
