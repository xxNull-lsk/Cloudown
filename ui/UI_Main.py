#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.UI_DownloadList import *
from ui.UI_Setting import UiSetting
from ui.UI_NewTask import UiNewTask
from ui.UI_TaskDetails import UiTaskDetails
from ui.UI_About import UiAbout
from urllib.error import *
import logging


class UiCommandList(QLabel):
    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        top = QVBoxLayout()
        top.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        top.setSpacing(0)
        top.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top)

        bottom = QVBoxLayout()
        bottom.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        bottom.setSpacing(0)
        bottom.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(bottom)

        self.top_list = QListWidget()
        self.top_list.setObjectName('CommandList')
        self.top_list.setFrameShape(QListWidget.NoFrame)
        self.top_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.top_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.top_list.currentRowChanged.connect(self._top_current_row_changed)
        self.top_list.itemClicked.connect(self._item_clicked)
        top.addWidget(self.top_list)

        self.bottom_list = QListWidget()
        self.bottom_list.setObjectName('CommandList')
        self.bottom_list.setFrameShape(QListWidget.NoFrame)
        self.bottom_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bottom_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bottom_list.currentRowChanged.connect(self._bottom_current_row_changed)
        self.bottom_list.itemClicked.connect(self._item_clicked)
        bottom.addWidget(self.bottom_list)

    def add_top_button(self, object_name, text=''):
        item = QListWidgetItem()
        item.setSizeHint(QSize(self.width(), 64))
        self.top_list.addItem(item)
        label = QLabel(text)
        label.setObjectName(object_name)
        self.top_list.setItemWidget(item, label)

    def add_bottom_button(self, object_name, text=''):
        item = QListWidgetItem()
        item.setSizeHint(QSize(self.width(), 64))
        self.bottom_list.addItem(item)
        label = QLabel(text)
        label.setObjectName(object_name)
        self.bottom_list.setItemWidget(item, label)
        self.bottom_list.setFixedHeight(item.sizeHint().height() * self.bottom_list.count())

    def _item_clicked(self, item):
        if self.sender() == self.top_list:
            index = self.top_list.row(item)
            self._top_current_row_changed(index)
        elif self.sender() == self.bottom_list:
            index = self.bottom_list.row(item)
            self._bottom_current_row_changed(index)

    def _bottom_current_row_changed(self, index):
        self.currentRowChanged.emit(index + self.top_list.count())
        if self.top_list.currentItem() is not None:
            self.top_list.currentItem().setSelected(False)

    def _top_current_row_changed(self, index):
        self.currentRowChanged.emit(index)
        if self.bottom_list.currentItem() is not None:
            self.bottom_list.currentItem().setSelected(False)

    def setCurrentRow(self, index):
        if index < self.top_list.count():
            self.top_list.setCurrentRow(index)
        else:
            self.bottom_list.setCurrentRow(index - self.top_list.count())


class UiMain(QWidget):
    name = ''

    def __init__(self, name):
        super().__init__()
        self.setObjectName('UiMain')
        with open('./qss/ui_main.qss', 'r') as f:
            self.setStyleSheet(f.read())
        self.resize(1024, 768)
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
