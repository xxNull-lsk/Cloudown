#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import gl


class UiNewTask(QWidget):
    aria2 = None
    bt_text = "拖放种子文件的到此处，或点击按钮选择种子文件"

    def __init__(self, parent):
        super(UiNewTask, self).__init__(parent)

        self.setObjectName('UiNewTask')
        self.setWindowTitle("新建任务")

        main_layout = QVBoxLayout(self)

        self.top_list = QTabWidget()
        self.top_list.tabBar().setObjectName("NewTaskTab")
        main_layout.addWidget(self.top_list)

        self.edit_url = QTextEdit()
        self.edit_url.setPlaceholderText("每行一个链接")
        self.top_list.addTab(self.edit_url, "下载链接")

        self.button_bt_file = QPushButton(self.bt_text)
        self.button_bt_file.setObjectName("SelectBtFile")
        self.button_bt_file.clicked.connect(self.on_select_bt_file)
        self.top_list.addTab(self.button_bt_file, "BT文件")

        download_options = QGridLayout()

        label_name = QLabel("重命名：")
        download_options.addWidget(label_name, 0, 0)
        self.edit_name = QLineEdit()
        download_options.addWidget(self.edit_name, 0, 1, 1, 3)

        label_name = QLabel("线程数：")
        download_options.addWidget(label_name, 0, 4)
        self.spin_thread_count = QSpinBox()
        download_options.addWidget(self.spin_thread_count, 0, 5)

        label_path = QLabel("保存位置：")
        download_options.addWidget(label_path, 1, 0)
        self.edit_save_path = QLineEdit()
        download_options.addWidget(self.edit_save_path, 1, 1, 1, 4)
        self.button_select_folder = QPushButton("...")
        self.button_select_folder.clicked.connect(self.on_select_folder)
        download_options.addWidget(self.button_select_folder, 1, 5)

        main_layout.addLayout(download_options)

        bottom_list = QHBoxLayout()
        bottom_list.setAlignment(Qt.AlignCenter)

        self.button_ok = QPushButton("确定")
        self.button_ok.setFixedHeight(32)
        self.button_ok.clicked.connect(self.on_ok)
        bottom_list.addWidget(self.button_ok)

        spacer = QSpacerItem(40, 32)
        bottom_list.addSpacerItem(spacer)

        button_cancel = QPushButton("取消")
        button_cancel.setFixedHeight(32)
        button_cancel.clicked.connect(self.close)
        bottom_list.addWidget(button_cancel)

        main_layout.addLayout(bottom_list)
        self._sync_status()
        gl.signals.value_changed.connect(self._value_changed)

    def _value_changed(self, name):
        if name == 'aria2':
            self._sync_status()

    def _sync_status(self):
        dm = gl.get_value('dm')
        self.aria2 = gl.get_value('aria2')
        if self.aria2 is None:
            options = None
        else:
            options = self.aria2.get_system_option()['result']
        if options is None:
            self.edit_save_path.setEnabled(False)
            self.spin_thread_count.setEnabled(False)
            self.edit_url.setEnabled(False)
            self.button_bt_file.setEnabled(False)
            self.edit_name.setEnabled(False)
            self.button_ok.setEnabled(False)
            self.button_select_folder.setEnabled(False)
        else:
            self.edit_save_path.setText(options['dir'])
            self.spin_thread_count.setValue(int(options['max-concurrent-downloads']))
        if not dm.settings.values['IS_LOCALE']:
            self.button_select_folder.setEnabled(False)

        self.setWindowModality(Qt.ApplicationModal)

    def on_select_folder(self):
        self.edit_save_path.setText(QFileDialog.getExistingDirectory(self, "选取文件夹", "./"))

    def on_select_bt_file(self):
        files = QFileDialog.getOpenFileName(self,
                                            "选取BT文件",
                                            "./",
                                            "BT Files (*.torrent);;All Files (*)")
        if len(files) >= 1 and files[0] != '':
            self.button_bt_file.setText(files[0])

    def close(self):
        dm = gl.get_value('dm')
        dm.main_wnd.left_widget.setCurrentRow(0)
        super(UiNewTask, self).close()

    def on_ok(self):
        save_path = self.edit_save_path.text()
        if self.top_list.currentIndex() == 0:
            urls = self.edit_url.toPlainText().split('\n')
            if len(urls) <= 0:
                return
            for url in urls:
                self.aria2.add_uri(url, save_path, False, self.spin_thread_count.value())
            self.edit_url.setText('')
        else:
            bt_file = self.button_bt_file.text()
            if self.bt_text == bt_file:
                return
            self.aria2.add_torrent(bt_file)
            self.button_select_folder.setText(self.bt_text)

        self.aria2.save_session()
        self.close()
