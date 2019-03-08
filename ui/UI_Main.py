#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.UI_DownloadList import *
from ui.UI_Setting import UiSetting
from ui.UI_NewTask import UiNewTask
from ui.UI_TaskDetails import UiTaskDetails
from ui.UI_About import UiAbout
from urllib.error import *
import logging


class UiCommandList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QListWidget.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def add_top_button(self, object_name):
        item = QListWidgetItem()
        item.setSizeHint(QSize(self.width(), 64))
        self.addItem(item)
        label = QLabel()
        label.setObjectName(object_name)
        self.setItemWidget(item, label)

    def add_bottom_button(self, object_name):
        self.add_top_button(object_name)


class UiMain(QWidget):
    name = ''

    def __init__(self, name):
        super().__init__()
        self.setObjectName('UiMain')
        with open('./qss/ui_main.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.resize(960, 600)
        self.name = name
        self.update_window_title()
        self.root_layout = QStackedLayout(self)
        label = QLabel()

        self.main_layout = QHBoxLayout()
        label.setLayout(self.main_layout)
        self.root_layout.addWidget(label)
        self.ui_details = UiTaskDetails(self)
        self.root_layout.addWidget(self.ui_details)
        self.root_layout.setCurrentIndex(0)

        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.left_widget = UiCommandList()
        self.left_widget.setObjectName('CommandList')
        self.left_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.ui_download_list = UiDownloadList(self)
        self.right_widget.addWidget(self.ui_download_list)

        self.ui_new_task = UiNewTask(self)
        self.right_widget.addWidget(self.ui_new_task)

        self.ui_setting = UiSetting(self)
        self.right_widget.addWidget(self.ui_setting)

        self.ui_about = UiAbout(self)
        self.right_widget.addWidget(self.ui_about)

        self.main_layout.addWidget(self.right_widget)

        self._setup_ui()
        self.left_widget.setCurrentRow(0)

        self.t = QTimer()
        self.t.setInterval(1000)
        self.t.timeout.connect(self._task_refresh)
        gl.signals.value_changed.connect(self._value_changed)

    def _value_changed(self, name):
        if name == 'aria2':
            self.update_window_title()

    def update_window_title(self):
        aria2 = gl.get_value('aria2')
        if aria2 is None:
            name = self.name + '（离线）'
        else:
            dm = gl.get_value('dm')
            if dm.settings.values['IS_LOCALE']:
                name = self.name + '（本地）'
            else:
                name = self.name + '（{}）'.format(dm.settings.values['REMOTE']["SERVER_ADDRESS"])
        super().setWindowTitle(name)

    def _setup_ui(self):
        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)

        list_name = ['download_list', 'new_task']
        for i in range(0, len(list_name)):
            self.left_widget.add_top_button(list_name[i])

        list_name = ['settings', 'about']
        for i in range(0, len(list_name)):
            self.left_widget.add_bottom_button(list_name[i])

    def show_details(self, task):
        self.ui_details.update_task(task)
        self.root_layout.setCurrentIndex(1)

    def show_normal(self):
        self.root_layout.setCurrentIndex(0)

    def show(self):
        super().show()
        self.show_normal()
        self.t.start()
        self._task_refresh()

    def hide(self):
        super().hide()
        self.t.stop()

    def _task_refresh(self):
        aria2 = gl.get_value('aria2')
        if aria2 is None:
            return
        try:
            ret = aria2.get_active_tasks()
            if ret is not None:
                self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_download)

            ret = aria2.get_waiting_tasks()
            if ret is not None:
                self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_waiting)

            ret = aria2.get_stopped_tasks()
            if ret is not None:
                self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_stopped)
        except URLError as err:
            logging.error('_refresh_task: {}'.format(err))
            gl.set_value('aria2', None)
            self.ui_download_list.set_tasks([], UiDownloadList.task_type_download)
            self.ui_download_list.set_tasks([], UiDownloadList.task_type_waiting)
            self.ui_download_list.set_tasks([], UiDownloadList.task_type_stopped)
            message = "{}\n是否重启或者重连aria2？".format(str(err.reason))
            ret = QMessageBox.critical(self, '服务器异常', message, QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.Yes:
                dm = gl.get_value('dm')
                dm.init_aria2()
