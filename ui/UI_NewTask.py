#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import gl
import os
import logging


class UiBtButton(QPushButton):
    def __init__(self, title='', parent=None):
        super(UiBtButton, self).__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            for url in e.mimeData().urls():
                exts = os.path.splitext(url.toLocalFile())
                if len(exts) != 2:
                    continue
                if exts[1] != '.torrent':
                    continue
                e.accept()
                break
        else:
            e.ignore()

    def dropEvent(self, e):
        files = ''
        for url in e.mimeData().urls():
            exts = os.path.splitext(url.toLocalFile())
            if len(exts) != 2:
                continue
            if exts[1] != '.torrent':
                continue
            files = files + url.toLocalFile() + '\n'
        self.setText(files)


class UiNewTask(QLabel):
    aria2 = None
    bt_button_title = ""

    def __init__(self, parent):
        super(UiNewTask, self).__init__(parent)

        self.setObjectName('UiNewTask')

        main_layout = QVBoxLayout(self)

        self.top_list = QTabWidget()
        self.top_list.tabBar().setObjectName("NewTaskTab")
        main_layout.addWidget(self.top_list)

        self.edit_url = QTextEdit()
        self.top_list.addTab(self.edit_url, self.tr("URL"))

        self.button_bt_file = UiBtButton()
        self.button_bt_file.setObjectName("SelectBtFile")
        self.button_bt_file.clicked.connect(self.on_select_bt_file)
        self.top_list.addTab(self.button_bt_file, self.tr("BT"))

        self.page_ftp = QWidget()
        self.top_list.addTab(self.page_ftp, self.tr("FTP"))

        page_ftp_layout = QGridLayout(self.page_ftp)
        self.label_ftp_url = QLabel()
        page_ftp_layout.addWidget(self.label_ftp_url, 0, 0)
        self.edit_ftp_url = QTextEdit()
        page_ftp_layout.addWidget(self.edit_ftp_url, 0, 1, 1, 5)

        self.label_ftp_username = QLabel()
        page_ftp_layout.addWidget(self.label_ftp_username, 1, 0)
        self.edit_ftp_username = QLineEdit()
        self.edit_ftp_username.setFixedWidth(240)
        page_ftp_layout.addWidget(self.edit_ftp_username, 1, 1)

        self.label_ftp_password = QLabel()
        page_ftp_layout.addWidget(self.label_ftp_password, 1, 2)
        self.edit_ftp_password = QLineEdit()
        self.edit_ftp_password.setEchoMode(QLineEdit.Password)
        self.edit_ftp_password.setFixedWidth(240)
        page_ftp_layout.addWidget(self.edit_ftp_password, 1, 3)

        self.page_sftp = QWidget()
        self.top_list.addTab(self.page_sftp, self.tr("SFTP"))

        page_sftp_layout = QGridLayout(self.page_sftp)
        self.label_sftp_ip = QLabel()
        page_sftp_layout.addWidget(self.label_sftp_ip, 0, 0)
        self.edit_sftp_ip = QLineEdit()
        self.edit_sftp_ip.setFixedWidth(240)
        page_sftp_layout.addWidget(self.edit_sftp_ip, 0, 1, 1, 2)

        self.label_sftp_port = QLabel()
        page_sftp_layout.addWidget(self.label_sftp_port, 0, 3)
        self.edit_sftp_port = QSpinBox()
        self.edit_sftp_port.setMinimum(0)
        self.edit_sftp_port.setMaximum(65535)
        self.edit_sftp_port.setValue(22)
        self.edit_sftp_port.setFixedWidth(160)
        page_sftp_layout.addWidget(self.edit_sftp_port, 0, 4)

        self.label_sftp_username = QLabel()
        page_sftp_layout.addWidget(self.label_sftp_username, 1, 0)
        self.edit_sftp_username = QLineEdit()
        self.edit_sftp_username.setFixedWidth(240)
        page_sftp_layout.addWidget(self.edit_sftp_username, 1, 1, 1, 2)

        self.label_sftp_password = QLabel()
        page_sftp_layout.addWidget(self.label_sftp_password, 1, 3)
        self.edit_sftp_password = QLineEdit()
        self.edit_sftp_password.setEchoMode(QLineEdit.Password)
        self.edit_sftp_password.setFixedWidth(160)
        page_sftp_layout.addWidget(self.edit_sftp_password, 1, 4)

        self.edit_sftp_url = QTextEdit()
        page_sftp_layout.addWidget(self.edit_sftp_url, 2, 0, 1, 6)

        download_options = QGridLayout()

        self.label_rename = QLabel()
        download_options.addWidget(self.label_rename, 0, 0)
        self.edit_name = QLineEdit()
        download_options.addWidget(self.edit_name, 0, 1, 1, 3)

        self.label_thread_count = QLabel()
        download_options.addWidget(self.label_thread_count, 0, 4)
        self.spin_thread_count = QSpinBox()
        download_options.addWidget(self.spin_thread_count, 0, 5)

        self.label_path = QLabel()
        download_options.addWidget(self.label_path, 1, 0)
        self.edit_save_path = QLineEdit()
        download_options.addWidget(self.edit_save_path, 1, 1, 1, 4)
        self.button_select_folder = QPushButton()
        self.button_select_folder.clicked.connect(self.on_select_folder)
        download_options.addWidget(self.button_select_folder, 1, 5)

        main_layout.addLayout(download_options)

        bottom_list = QHBoxLayout()
        bottom_list.setAlignment(Qt.AlignCenter)

        self.button_ok = QPushButton()
        self.button_ok.setFixedHeight(32)
        self.button_ok.clicked.connect(self.on_ok)
        bottom_list.addWidget(self.button_ok)

        spacer = QSpacerItem(40, 32)
        bottom_list.addSpacerItem(spacer)

        self.button_cancel = QPushButton()
        self.button_cancel.setFixedHeight(32)
        self.button_cancel.clicked.connect(self.close)
        bottom_list.addWidget(self.button_cancel)

        main_layout.addLayout(bottom_list)
        self.update_ui()
        self._sync_status()
        gl.signals.value_changed.connect(self._value_changed)

    def update_ui(self):
        self.setWindowTitle(self.tr("New Task"))

        self.top_list.setTabText(0, self.tr("URL"))
        self.top_list.setTabText(1, self.tr("BT"))
        self.top_list.setTabText(2, self.tr("FTP"))
        self.top_list.setTabText(3, self.tr("SFTP"))

        self.bt_button_title = self.tr('Drop BT file(s) in here, or click this button to select BT file(s)')
        self.button_bt_file.setText(self.bt_button_title)
        self.edit_url.setPlaceholderText(
            self.tr("If add multiples tasks, be sure one task URL pre line. \
support HTTP, HTTPS, FTP and magnet..."))

        self.label_ftp_url.setText(self.tr("URL:"))
        self.edit_ftp_url.setPlaceholderText(
            self.tr("If add multiples tasks, be sure one task URL pre line. \
only support FTP which use the same username and password"))

        self.label_ftp_username.setText(self.tr("UserName:"))  # anonymous
        self.edit_ftp_username.setPlaceholderText(self.tr("anonymous"))
        self.label_ftp_password.setText(self.tr("Password:"))

        self.label_sftp_ip.setText(self.tr("IP:"))
        self.label_sftp_port.setText(self.tr("Port:"))
        self.edit_sftp_url.setPlaceholderText(self.tr("One file per line, if you add multiple files"))

        self.label_sftp_username.setText(self.tr("UserName:"))
        self.label_sftp_password.setText(self.tr("Password:"))

        self.label_rename.setText(self.tr("Rename:"))
        self.label_thread_count.setText(self.tr("Thread count:"))
        self.label_path.setText(self.tr("Save path:"))
        self.label_path.setText(self.tr("Save path:"))
        self.button_select_folder.setText(self.tr("..."))
        self.button_select_folder.setText(self.tr("..."))
        self.button_ok.setText(self.tr("OK"))
        self.button_cancel.setText(self.tr("Cancel"))
        pass

    def _value_changed(self, v):
        if v['name'] == 'aria2':
            self._sync_status()
        elif v['name'] == 'language':
            self.update_ui()

    def _sync_status(self):
        dm = gl.get_value('dm')
        self.aria2 = gl.get_value('aria2')
        options = None
        if self.aria2 is not None:
            ret = self.aria2.get_system_option()
            if ret is not None:
                options = ret['result']
        is_enable = False
        if options is not None:
            is_enable = True
            self.edit_save_path.setText(options['dir'])
            self.spin_thread_count.setValue(int(options['max-concurrent-downloads']))

        self.edit_save_path.setEnabled(is_enable)
        self.spin_thread_count.setEnabled(is_enable)
        self.edit_url.setEnabled(is_enable)
        self.button_bt_file.setEnabled(is_enable)
        self.edit_name.setEnabled(is_enable)
        self.button_ok.setEnabled(is_enable)
        self.button_select_folder.setEnabled(is_enable)

        if not dm.settings.values['IS_LOCALE']:
            self.button_select_folder.setEnabled(False)

        self.setWindowModality(Qt.ApplicationModal)

    def on_select_folder(self):
        self.edit_save_path.setText(QFileDialog.getExistingDirectory(self, self.tr("Select folder"), "./"))

    def on_select_bt_file(self):
        files = QFileDialog.getOpenFileName(self,
                                            self.tr("Select BT files"),
                                            "./",
                                            "BT Files (*.torrent);;All Files (*)")
        if len(files) >= 1 and files[0] != '':
            msg = ''
            for f in files:
                msg = msg + f + '\n'
            self.button_bt_file.setText(msg)

    def close(self):
        dm = gl.get_value('dm')
        dm.main_wnd.left_widget.setCurrentRow(0)
        super(UiNewTask, self).close()

    def on_ok(self):
        params = {
            'dir': self.edit_save_path.text(),
            'max-concurrent-downloads': self.spin_thread_count.value()
        }
        if self.top_list.currentIndex() == 0:
            urls = self.edit_url.toPlainText().split('\n')
            if len(urls) <= 0:
                return
            for url in urls:
                if len(url) <= 0:
                    continue
                self.aria2.add_uri(url, params=params)
            self.edit_url.setText('')
        elif self.top_list.currentIndex() == 1:
            bt_files = self.button_bt_file.text()
            if self.bt_button_title == bt_files:
                return
            bt_files = bt_files.split('\n')
            for f in bt_files:
                if not os.path.exists(f):
                    continue
                self.aria2.add_torrent(f)
            self.button_select_folder.setText(self.bt_button_title)
        elif self.top_list.currentIndex() == 2:  # FTP
            urls = self.edit_ftp_url.toPlainText().split('\n')
            if len(urls) <= 0:
                return
            username = self.edit_ftp_username.text()
            if username == '':
                username = 'anonymous'
            params['ftp-user'] = username
            params['ftp-passwd'] = self.edit_ftp_password.text()
            for url in urls:
                if len(url) <= 0:
                    continue
                try:
                    self.aria2.add_uri(url, params=params)
                except Exception as err:
                    logging.error('Add ftp file error: {0}'.format(err))
                    QMessageBox.warning(self, self.tr("Warn"), self.tr("URL error, do you want to continue?"),
                                        QMessageBox.Yes | QMessageBox.No)
            self.edit_ftp_url.setText('')
            self.edit_ftp_username.setText('')
            self.edit_ftp_password.setText('')
        elif self.top_list.currentIndex() == 3:  # SFTP
            files = self.edit_sftp_url.toPlainText().split('\n')
            if len(files) <= 0:
                return
            ip = self.edit_sftp_ip.text()
            port = self.edit_sftp_port.text()
            username = self.edit_sftp_username.text()
            password = self.edit_sftp_password.text()

            # sftp://allan:zhengqian@118.25.17.65:22/home/allan/frp_0.24.1_linux_amd64.tar.gz
            for f in files:
                if len(f) <= 0:
                    continue
                url = 'sftp://{0}:{1}@{2}:{3}{4}'.format(username, password, ip, port, f)
                try:
                    self.aria2.add_uri(url, params=params)
                except Exception as err:
                    logging.error('Add sftp file error: {0}'.format(err))
                    QMessageBox.warning(self, self.tr("Warn"), self.tr("URL error, do you want to continue?"),
                                        QMessageBox.Yes | QMessageBox.No)
            self.edit_sftp_url.setText('')

        self.aria2.save_session()
        self.close()

    def set_url(self, urls):
        if urls is None:
            return
        text = self.edit_url.toPlainText()
        for url in urls:
            if text != '':
                text = text + '\n'
            text = text + url
        self.edit_url.setText(text)
        self.top_list.setCurrentIndex(0)
