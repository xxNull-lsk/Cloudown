#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import json
import gl


class SystemSettings:
    values = {
        # 'SERVER_URL': 'http://118.25.17.65:6800/jsonrpc',
        'IS_LOCALE': False,
        'ARIA2': './aria2',
        'PARAMS': [
            '--conf-path="${START_FOLDER}/aria2.conf"',
            '--input-file="${START_FOLDER}/aria2.session"',
            '--save-session="${START_FOLDER}/aria2.session"',
            '--dht-file-path="${START_FOLDER}/dht.dat"',
            '--dht-file-path6="${START_FOLDER}/dht6.dat"',
            '--quiet=true'],
        'DOWNLOAD_DIR': '${DOWNLOAD}',
        'SERVER_URL': 'http://192.168.2.100:6800/jsonrpc',
        'SERVER_TOKEN': 'allan',
        'REFRESH': 1
    }
    file = 'setting.json'

    def load(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, 'r') as f:
            self.values = json.loads(f.read())

    def save(self):
        if self.file is None:
            return False
        with open(self.file, 'w+') as f:
            f.write(json.dumps(self.values, indent=4))
        return True


class UiSetting(QWidget):

    def __init__(self, parent):
        super(UiSetting, self).__init__(parent)
        self.settings = parent.download_manager.settings
        self.setObjectName('UiSetting')
        
        self.setWindowTitle("配置")

        self.main_layout = QGridLayout(self)

        label_refresh = QLabel("刷新频率：")
        row = 0
        label_refresh.setFixedHeight(28)
        self.main_layout.addWidget(label_refresh, row, 0)
        self.spin_refresh = QSpinBox()
        self.spin_refresh.setFixedHeight(28)
        self.spin_refresh.setMinimum(1)
        self.spin_refresh.setMaximum(60)
        self.spin_refresh.setValue(self.settings.values['REFRESH'])
        self.main_layout.addWidget(self.spin_refresh, row, 1)
        label_sec = QLabel('秒')
        self.main_layout.addWidget(label_sec, row, 2)
        row = row + 1

        self.radio_local = QRadioButton("本地下载")
        self.radio_local.clicked.connect(self.on_change_type)
        self.main_layout.addWidget(self.radio_local, row, 0)
        row = row + 1

        label_name = QLabel('Aric2地址：')
        self.main_layout.addWidget(label_name, row, 1, 1, 2)
        self.edit_aria2 = QLineEdit()
        self.edit_aria2.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_aria2, row, 2, 1, 2)
        self.button_select_aria = QPushButton('...')
        self.button_select_aria.setFixedHeight(28)
        self.button_select_aria.clicked.connect(self.on_select_aria)
        self.main_layout.addWidget(self.button_select_aria, row, 4)
        row = row + 1

        label_name = QLabel("下载目录")
        self.main_layout.addWidget(label_name, row, 1)
        self.edit_download_folder = QLineEdit()
        self.main_layout.addWidget(self.edit_download_folder, row, 2)
        self.button_select_download_folder = QPushButton("...")
        self.button_select_download_folder.clicked.connect(self.on_change_download_path)
        self.main_layout.addWidget(self.button_select_download_folder, row, 3)
        row = row + 1

        label_name = QLabel('Aric2参数：')
        self.main_layout.addWidget(label_name, row, 1, 1, 2, Qt.AlignTop)
        # row = row + 1
        self.edit_aria2_params = QTextEdit()
        self.main_layout.addWidget(self.edit_aria2_params, row, 2, 1, 3)
        row = row + 1

        self.radio_remote = QRadioButton("远程下载")
        self.radio_remote.clicked.connect(self.on_change_type)
        self.main_layout.addWidget(self.radio_remote, row, 0)
        row = row + 1

        self.main_layout.setContentsMargins(60, 60, 20, 20)
        label_url = QLabel("服务器URL：")
        label_url.setFixedHeight(28)
        self.main_layout.addWidget(label_url, row, 1)
        self.edit_url = QLineEdit(self.settings.values['SERVER_URL'])
        self.edit_url.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_url, row, 2, 1, 3)
        row = row + 1

        label_token = QLabel("服务器token：")
        label_token.setFixedHeight(28)
        self.main_layout.addWidget(label_token, row, 1)
        self.edit_token = QLineEdit(self.settings.values['SERVER_TOKEN'])
        self.edit_token.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_token, row, 2, 1, 2)
        row = row + 1

        self.button_ok = QPushButton("确定")
        self.button_ok.setFixedHeight(32)
        self.button_ok.clicked.connect(self.on_ok)
        self.main_layout.addWidget(self.button_ok, row, 1)

        button_cancel = QPushButton("取消")
        button_cancel.setFixedHeight(32)
        button_cancel.clicked.connect(self.close)
        self.main_layout.addWidget(button_cancel, row, 3)

        self.setWindowModality(Qt.ApplicationModal)

        self.edit_aria2.setText(self.settings.values['ARIA2'])
        self.radio_local.setChecked(self.settings.values['IS_LOCALE'])
        self.radio_remote.setChecked(not self.settings.values['IS_LOCALE'])
        params = ''
        for p in self.settings.values['PARAMS']:
            if params != '':
                params = params + '\n'
            params = params + p
        self.edit_aria2_params.setText(params)
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder = self.settings.values["DOWNLOAD_DIR"]
        folder = folder.replace('${DOWNLOAD}', download_path)
        self.edit_download_folder.setText(folder)
        self.on_change_type()

    def on_change_type(self):
        self.edit_download_folder.setEnabled(self.radio_local.isChecked())
        self.button_select_download_folder.setEnabled(self.radio_local.isChecked())
        self.edit_aria2_params.setEnabled(self.radio_local.isChecked())
        self.button_select_aria.setEnabled(self.radio_local.isChecked())
        self.edit_aria2.setEnabled(self.radio_local.isChecked())
        self.edit_url.setEnabled(self.radio_remote.isChecked())
        self.edit_token.setEnabled(self.radio_remote.isChecked())

    def close(self):
        dm = gl.get_value('dm')
        dm.main_wnd.left_widget.setCurrentRow(0)
        super(UiSetting, self).close()

    def on_ok(self):
        self.settings.values["REFRESH"] = self.spin_refresh.value()
        self.settings.values["SERVER_TOKEN"] = self.edit_token.text()
        self.settings.values["IS_LOCALE"] = self.radio_local.isChecked()
        self.settings.values['ARIA2'] = self.edit_aria2.text()
        params = self.edit_aria2_params.toPlainText()
        self.settings.values['PARAMS'].clear()
        for line in params.split('\n'):
            self.settings.values['PARAMS'].append(line)
        self.settings.values["DOWNLOAD_DIR"] = self.edit_download_folder.text()
        self.settings.save()
        self.close()

    def on_select_aria(self):
        folder = QFileDialog.getExistingDirectory(self,
                                                  "选择Aria2所在目录",
                                                  self.settings.values["ARIA2"])
        if folder is None:
            return
        self.edit_aria2.setText(folder)

    def on_change_download_path(self):
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder = self.settings.values["DOWNLOAD_DIR"]
        folder = folder.replace('${DOWNLOAD}', download_path)
        folder = QFileDialog.getExistingDirectory(self,
                                                  "选择下载目录",
                                                  folder)
        if folder is None:
            return
        self.edit_download_folder.setText(folder)
