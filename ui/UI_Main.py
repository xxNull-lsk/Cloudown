#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.UI_DownloadList import *
from ui.UI_Setting import UiSetting
from ui.UI_NewTask import UiNewTask
from ui.UI_TaskDetails import UiTaskDetails
from urllib.error import *
import logging


class UiMain(QWidget):
    name = ''

    def __init__(self, name):
        super(UiMain, self).__init__()
        self.setObjectName('UiMain')
        with open('./qss/ui_main.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.resize(960, 600)
        self.name = name
        self.updateWindowTitle()
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

        self.left_widget = QListWidget()
        self.left_widget.setObjectName('CommandList')

        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.ui_download_list = UiDownloadList(self)
        self.right_widget.addWidget(self.ui_download_list)

        self.ui_new_task = UiNewTask(self)
        self.right_widget.addWidget(self.ui_new_task)

        self.ui_setting = UiSetting(self)
        self.right_widget.addWidget(self.ui_setting)

        self.main_layout.addWidget(self.right_widget)

        self._setup_ui()
        self.left_widget.setCurrentRow(0)

        self.t = QTimer()
        self.t.setInterval(1000)
        self.t.timeout.connect(self._task_refresh)
        gl.signals.value_changed.connect(self._value_changed)

    def _value_changed(self, name):
        if name == 'aria2':
            self.updateWindowTitle()

    def updateWindowTitle(self):
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
        self.left_widget.setFrameShape(QListWidget.NoFrame)
        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        list_name = ['download_list', 'new_task', 'settings']
        for i in range(0, len(list_name)):
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.left_widget.width(), 64))
            self.left_widget.addItem(item)

            label = QLabel()
            label.setObjectName(list_name[i])
            self.left_widget.setItemWidget(item, label)

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
