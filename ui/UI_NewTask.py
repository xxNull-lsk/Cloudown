#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import gl


class UiNewTask(QWidget):
    def __init__(self, parent):
        super(UiNewTask, self).__init__(parent)
        self.aria2 = gl.get_value('aria2')
        self.setObjectName('UiNewTask')
        
        self.setWindowTitle("新建任务")

        self.main_layout = QVBoxLayout(self)

        self.top_list = QTabWidget()
        with open("./qss/ui_new_task_tab.qss", 'r') as f:
            self.top_list.setStyleSheet(f.read())
        self.main_layout.addWidget(self.top_list)

        self.edit_url = QTextEdit()
        self.top_list.addTab(self.edit_url, "下载链接")

        self.button_bt_file = QPushButton("拖放种子文件的到此处，或点击按钮选择种子文件")
        self.button_bt_file.clicked.connect(self.on_select_bt_file)
        with open("./qss/ui_bt_button.qss", 'r') as f:
            self.button_bt_file.setStyleSheet(f.read())
        self.top_list.addTab(self.button_bt_file, "BT文件")

        options = self.aria2.get_system_option()
        with open('./aria.conf', 'w+') as f:
            f.write(json.dumps(options, indent=4))
        download_options = QGridLayout()
        label_name = QLabel("重命名：")
        download_options.addWidget(label_name, 0, 0)
        self.edit_name = QLineEdit()
        download_options.addWidget(self.edit_name, 0, 1, 1, 3)
        label_name = QLabel("线程数：")
        download_options.addWidget(label_name, 0, 4)
        self.spin_thread_count = QSpinBox()
        self.spin_thread_count.setValue(int(options['result']['max-concurrent-downloads']))
        download_options.addWidget(self.spin_thread_count, 0, 5)

        label_path = QLabel("保存位置：")
        download_options.addWidget(label_path, 1, 0)
        self.edit_save_path = QLineEdit(options['result']['dir'])
        download_options.addWidget(self.edit_save_path, 1, 1, 1, 4)
        button_select_folder = QPushButton("...")
        button_select_folder.clicked.connect(self.on_select_folder)
        download_options.addWidget(button_select_folder, 1, 5)

        self.main_layout.addLayout(download_options)

        self.bottom_list = QHBoxLayout()
        self.bottom_list.setAlignment(Qt.AlignCenter)

        button_ok = QPushButton("确定")
        button_ok.setFixedHeight(32)
        button_ok.clicked.connect(self.on_ok)
        self.bottom_list.addWidget(button_ok)

        spacer = QSpacerItem(40, 32)
        self.bottom_list.addSpacerItem(spacer)

        button_cancel = QPushButton("取消")
        button_cancel.setFixedHeight(32)
        button_cancel.clicked.connect(self.close)
        self.bottom_list.addWidget(button_cancel)

        self.main_layout.addLayout(self.bottom_list)

        self.setWindowModality(Qt.ApplicationModal)

    def on_select_folder(self):
        self.edit_save_path.setText(QFileDialog.getExistingDirectory(self, "选取文件夹", "./"))

    def on_select_bt_file(self):
        files = QFileDialog.getOpenFileName(self,
                                            "选取BT文件",
                                            "./",
                                            "BT Files (*.bt);;All Files (*)")
        if len(files) >= 1 and files[0] != '':
            self.button_bt_file.setText(files[0])

    def close(self):
        dm = gl.get_value('dm')
        dm.main_wnd.left_widget.setCurrentRow(0)
        super(UiNewTask, self).close()

    def on_ok(self):
        save_path = self.edit_save_path.text()
        urls = self.edit_url.toPlainText().split('\n')
        for url in urls:
            self.aria2.add_uri(url, save_path)
        self.close()
