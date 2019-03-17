#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import locale
import sys
import json
import gl
from ui.Misc import *


class SystemSettings:
    values = {
        'IS_LOCALE': True,
        'SKIN': 'Color',
        'SKINS': ['Color', 'Black', 'TechBlack'],
        'LANGUAGE': 0,
        'LANGUAGES': [
            {'NAME': 'OS Language', 'FILE_NAME': ''},
            {'NAME': 'zh_CN 简体中文', 'FILE_NAME': 'zh_CN'},
            {'NAME': 'en English', 'FILE_NAME': 'en'},
        ],
        'LOCALE': {
            'ARIA2': './aria2/aria2c.exe',
            'PARAMS': [
                '--conf-path="${DATA_PATH}/aria2.conf"',
                '--input-file="${DATA_PATH}/aria2.session"',
                '--save-session="${DATA_PATH}/aria2.session"',
                '--dht-file-path="${DATA_PATH}/dht.dat"',
                '--dht-file-path6="${DATA_PATH}/dht6.dat"',
                '--quiet=true'],
            'DOWNLOAD_DIR': '${DOWNLOAD_PATH}',
            'SERVER_PORT': '8160',
            'SERVER_TOKEN': 'air_download',
            'KEEP_RUNNING': True
        },
        'REMOTE': {
            'SERVER_ADDRESS': '127.0.0.1:6800',  # '192.168.2.100:6800',
            'SERVER_TOKEN': 'air_download',
            'SERVER_HISTORY': [
                {'addr': '127.0.0.1:6800', 'token': 'air_download'},
            ]
        },
        'REFRESH': 1
    }
    file = './data/setting.json'

    def __init__(self):
        self.file = translate_macro('${DATA_PATH}/setting.json')
        if sys.platform == 'linux':
            self.values['LOCALE']['ARIA2'] = './aria2/aria2c'

    def load(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, 'r') as f:
            values = json.loads(f.read())
            merged_dict(self.values, values)

    def save(self):
        if self.file is None:
            return False
        with open(self.file, 'w+') as f:
            f.write(json.dumps(self.values, indent=4))
        return True


class UiSetting(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        dm = gl.get_value('dm')
        self.settings = dm.settings
        self.setObjectName('UiSetting')
        
        self.setWindowTitle(self.tr("Settings"))

        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(60, 60, 20, 20)
        row = 0

        self.label_language = QLabel()
        self.label_language.setFixedHeight(28)
        self.main_layout.addWidget(self.label_language, row, 0)
        self.combox_language = QComboBox()
        self.combox_language.setFixedHeight(28)
        self.main_layout.addWidget(self.combox_language, row, 1)
        row = row + 1

        self.label_skin = QLabel()
        self.label_skin.setFixedHeight(28)
        self.main_layout.addWidget(self.label_skin, row, 0)
        self.combox_skin = QComboBox()
        self.combox_skin.setFixedHeight(28)
        self.main_layout.addWidget(self.combox_skin, row, 1)
        row = row + 1

        self.label_refresh = QLabel()
        self.label_refresh.setFixedHeight(28)
        self.main_layout.addWidget(self.label_refresh, row, 0)
        self.spin_refresh = QSpinBox()
        self.spin_refresh.setFixedHeight(28)
        self.spin_refresh.setMinimum(1)
        self.spin_refresh.setMaximum(60)
        self.spin_refresh.setValue(self.settings.values['REFRESH'])
        self.main_layout.addWidget(self.spin_refresh, row, 1)
        self.label_sec = QLabel()
        self.main_layout.addWidget(self.label_sec, row, 2)
        row = row + 1

        self.radio_remote = QRadioButton()
        self.radio_remote.clicked.connect(self.on_changed_type)
        self.main_layout.addWidget(self.radio_remote, row, 0)
        row = row + 1

        self.label_url = QLabel()
        self.label_url.setFixedHeight(28)
        self.main_layout.addWidget(self.label_url, row, 1)

        self.edit_remote_addr = QComboBox()  # QLineEdit(self.settings.values['REMOTE']['SERVER_ADDRESS'])
        self.edit_remote_addr.currentTextChanged.connect(self.on_changed_remote_addr)
        self.edit_remote_addr.setEditable(True)
        self.edit_remote_addr.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_remote_addr, row, 2, 1, 2)
        row = row + 1

        self.label_remote_token = QLabel()
        self.label_remote_token.setFixedHeight(28)
        self.main_layout.addWidget(self.label_remote_token, row, 1)
        self.edit_remote_token = QLineEdit(self.settings.values['REMOTE']['SERVER_TOKEN'])
        self.edit_remote_token.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_remote_token, row, 2, 1, 2)
        row = row + 1

        self.radio_local = QRadioButton()
        self.radio_local.clicked.connect(self.on_changed_type)
        self.main_layout.addWidget(self.radio_local, row, 0)
        row = row + 1

        self.label_port = QLabel()
        self.label_port.setFixedHeight(28)
        self.main_layout.addWidget(self.label_port, row, 1)
        self.edit_locale_port = QLineEdit(self.settings.values['LOCALE']['SERVER_PORT'])
        self.edit_locale_port.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_locale_port, row, 2, 1, 2)
        row = row + 1

        self.label_token = QLabel()
        self.label_token.setFixedHeight(28)
        self.main_layout.addWidget(self.label_token, row, 1)
        self.edit_locale_token = QLineEdit(self.settings.values['LOCALE']['SERVER_TOKEN'])
        self.edit_locale_token.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_locale_token, row, 2, 1, 2)
        row = row + 1

        self.label_aria2_path = QLabel()
        self.main_layout.addWidget(self.label_aria2_path, row, 1, 1, 2)
        self.edit_aria2 = QLineEdit()
        self.edit_aria2.setFixedHeight(28)
        self.main_layout.addWidget(self.edit_aria2, row, 2, 1, 2)
        self.button_select_aria = QPushButton('...')
        self.button_select_aria.setFixedHeight(28)
        self.button_select_aria.clicked.connect(self.on_select_aria)
        self.main_layout.addWidget(self.button_select_aria, row, 4)
        row = row + 1

        self.label_aria2_params = QLabel()
        self.main_layout.addWidget(self.label_aria2_params, row, 1, 1, 2, Qt.AlignTop)
        # row = row + 1
        self.edit_aria2_params = QTextEdit()
        self.main_layout.addWidget(self.edit_aria2_params, row, 2, 1, 3)
        row = row + 1

        self.label_save_path = QLabel()
        self.main_layout.addWidget(self.label_save_path, row, 1)
        self.edit_download_folder = QLineEdit()
        self.main_layout.addWidget(self.edit_download_folder, row, 2, 1, 2)
        self.button_select_download_folder = QPushButton()
        self.button_select_download_folder.clicked.connect(self.on_change_download_path)
        self.main_layout.addWidget(self.button_select_download_folder, row, 4)
        row = row + 1

        self.checkbox_keep_running = QCheckBox()
        self.main_layout.addWidget(self.checkbox_keep_running, row, 1, 1, 2, Qt.AlignTop)
        row = row + 1

        self.button_ok = QPushButton()
        self.button_ok.setFixedHeight(32)
        self.button_ok.clicked.connect(self.on_ok)
        self.main_layout.addWidget(self.button_ok, row, 1)

        self.button_cancel = QPushButton()
        self.button_cancel.setFixedHeight(32)
        self.button_cancel.clicked.connect(self.close)
        self.main_layout.addWidget(self.button_cancel, row, 3)

        self.setWindowModality(Qt.ApplicationModal)

        for url in self.settings.values['REMOTE']['SERVER_HISTORY']:
            self.edit_remote_addr.addItem(url['addr'])
        self.edit_remote_addr.setCurrentText(self.settings.values['REMOTE']['SERVER_ADDRESS'])

        self.edit_aria2.setText(self.settings.values['LOCALE']['ARIA2'])
        self.radio_local.setChecked(self.settings.values['IS_LOCALE'])
        self.radio_remote.setChecked(not self.settings.values['IS_LOCALE'])
        params = ''
        for p in self.settings.values['LOCALE']['PARAMS']:
            if params != '':
                params = params + '\n'
            params = params + p
        self.edit_aria2_params.setText(params)
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder = self.settings.values['LOCALE']["DOWNLOAD_DIR"]
        folder = folder.replace('${DOWNLOAD}', download_path)
        self.edit_download_folder.setText(folder)

        for language in self.settings.values['LANGUAGES']:
            self.combox_language.addItem(language['NAME'])
        curr_language = self.settings.values['LANGUAGE']
        self.combox_language.setCurrentText(self.settings.values['LANGUAGES'][curr_language]['NAME'])
        self.combox_language.currentIndexChanged.connect(self.on_lanugage_changed)

        self.settings.values['SKINS'].clear()
        for f in os.listdir('./skins'):
            if os.path.isdir(os.path.join('./skins', f)):
                self.settings.values['SKINS'].append(f)
        for skin in self.settings.values['SKINS']:
            index = self.combox_skin.count()
            self.combox_skin.addItem(self.tr(skin))
            self.combox_skin.setItemData(index, skin)
        self.combox_skin.setCurrentText(self.tr(self.settings.values['SKIN']))
        self.combox_skin.currentIndexChanged.connect(self.on_skin_changed)

        self.checkbox_keep_running.setChecked(self.settings.values['LOCALE']["KEEP_RUNNING"])
        self.on_changed_type()
        gl.signals.value_changed.connect(self.on_value_changed)
        self.update_ui()

    def on_skin_changed(self, index):
        text = self.combox_skin.itemData(index)
        gl.set_value('skin', text)

    def on_lanugage_changed(self, index):
        if index == 0:
            filename = locale.getdefaultlocale()[0]
        else:
            filename = self.settings.values['LANGUAGES'][index]['FILE_NAME']
        trans = QTranslator()
        if trans.load(os.path.join('languages', filename)):
            dm = gl.get_value('dm')
            old_language = gl.get_value('language')
            dm.app.removeTranslator(old_language)
            dm.app.installTranslator(trans)
            gl.set_value('language', trans)

    def on_value_changed(self, v):
        if v['name'] == 'language':
            self.update_ui()
        elif v['name'] == 'skin ':
            self.update_ui()

    def update_ui(self):
        self.button_cancel.setText(self.tr("Cancel"))
        self.button_ok.setText(self.tr("OK"))
        self.label_aria2_params.setText(self.tr('Aria2 parameters:'))
        self.label_save_path.setText(self.tr("Save path:"))
        self.button_select_download_folder.setText(self.tr("..."))
        self.label_aria2_path.setText(self.tr('Aria2 path:'))
        self.label_token.setText(self.tr("Token:"))
        self.label_port.setText(self.tr("Port:"))
        self.radio_local.setText(self.tr("Local"))
        self.label_remote_token.setText(self.tr("Token:"))
        self.label_url.setText(self.tr("Server address:"))
        self.radio_remote.setText(self.tr("Remote"))
        self.label_refresh.setText(self.tr("Refresh rate:"))
        self.label_sec.setText(self.tr('second(s)'))
        self.label_language.setText(self.tr("Language:"))
        self.checkbox_keep_running.setText(self.tr('Keep background downloads when closed this application'))

    def on_changed_remote_addr(self, text):
        for url in self.settings.values['REMOTE']['SERVER_HISTORY']:
            if text == url['addr']:
                self.edit_remote_token.setText(url['token'])
                break

    def on_changed_type(self):
        self.edit_download_folder.setEnabled(self.radio_local.isChecked())
        self.button_select_download_folder.setEnabled(self.radio_local.isChecked())
        self.edit_aria2_params.setEnabled(self.radio_local.isChecked())
        self.button_select_aria.setEnabled(self.radio_local.isChecked())
        self.edit_aria2.setEnabled(self.radio_local.isChecked())
        self.edit_locale_token.setEnabled(self.radio_local.isChecked())
        self.edit_locale_port.setEnabled(self.radio_local.isChecked())
        self.checkbox_keep_running.setEnabled(self.radio_local.isChecked())
        self.edit_remote_addr.setEnabled(self.radio_remote.isChecked())
        self.edit_remote_token.setEnabled(self.radio_remote.isChecked())

    def close(self):
        dm = gl.get_value('dm')
        dm.main_wnd.left_widget.setCurrentRow(0)

    def on_ok(self):
        self.settings.values['LANGUAGE'] = self.combox_language.currentIndex()
        self.settings.values["REFRESH"] = self.spin_refresh.value()

        self.settings.values["IS_LOCALE"] = self.radio_local.isChecked()

        url = {
            'addr': self.edit_remote_addr.currentText(),
            'token': self.edit_remote_token.text()
        }
        self.settings.values['REMOTE']["SERVER_ADDRESS"] = url['addr']
        self.settings.values['REMOTE']["SERVER_TOKEN"] = url['token']
        if url not in self.settings.values['REMOTE']['SERVER_HISTORY']:
            self.settings.values['REMOTE']['SERVER_HISTORY'].append(url)

        self.settings.values['LOCALE']["SERVER_PORT"] = self.edit_locale_port.text()
        self.settings.values['LOCALE']["SERVER_TOKEN"] = self.edit_locale_token.text()
        self.settings.values['LOCALE']['ARIA2'] = self.edit_aria2.text()
        params = self.edit_aria2_params.toPlainText()
        self.settings.values['LOCALE']['PARAMS'].clear()
        for line in params.split('\n'):
            self.settings.values['LOCALE']['PARAMS'].append(line)
        self.settings.values['LOCALE']["DOWNLOAD_DIR"] = self.edit_download_folder.text()
        self.settings.values['LOCALE']['KEEP_RUNNING'] = self.checkbox_keep_running.isChecked()

        self.settings.values['SKIN'] = self.combox_skin.itemData(self.combox_skin.currentIndex())
        self.settings.save()
        gl.set_value("settings", self.settings)
        dm = gl.get_value('dm')
        dm.init_aria2()
        dm.main_wnd.left_widget.setCurrentRow(0)

    def on_select_aria(self):
        file_filter = 'All Files(*)'
        if sys.platform == 'win32':
            file_filter = "Exec File(*.exe);;All Files (*)"
        files = QFileDialog.getOpenFileName(self,
                                            self.tr("Select aria2 path"),
                                            './',
                                            file_filter)
        if len(files) <= 0 or files[0] == '':
            return
        self.edit_aria2.setText(files[0])

    def on_change_download_path(self):
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        folder = self.settings.values['LOCALE']["DOWNLOAD_DIR"]
        folder = folder.replace('${DOWNLOAD}', download_path)
        folder = QFileDialog.getExistingDirectory(self,
                                                  self.tr("select save path"),
                                                  folder)
        if folder is None:
            return
        self.edit_download_folder.setText(folder)
