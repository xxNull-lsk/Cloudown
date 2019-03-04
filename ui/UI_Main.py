#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.UI_DownloadList import *
from ui.UI_Setting import UiSetting
from ui.UI_NewTask import UiNewTask
from ui.UI_TaskDetails import UiTaskDetails


class UiMain(QWidget):
    def __init__(self, name, download_manager):
        super(UiMain, self).__init__()
        self.setObjectName('UiMain')
        self.resize(960, 600)
        self.download_manager = download_manager
        
        self.setWindowTitle(name)
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
        # self.left_widget.setSpacing(5)

        with open('./qss/ui_main.qss', 'r') as f:
            self.left_widget.setStyleSheet(f.read())
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
        self.t.timeout.connect(self.task_refresh)

    def _setup_ui(self):
        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)
        self.left_widget.setFrameShape(QListWidget.NoFrame)
        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        list_icon = ['download_list.png', 'new_task.png', 'settings.png']
        for i in range(0, len(list_icon)):
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.left_widget.width(), 64))
            self.left_widget.addItem(item)
            label = QLabel()
            icon_file = "icons/{}".format(list_icon[i])
            label.setStyleSheet("QLabel{ image: url(%s); padding: 8px; }" % icon_file)
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
        self.task_refresh()

    def hide(self):
        super().hide()
        self.t.stop()

    def task_refresh(self):
        aria2 = gl.get_value('aria2')
        if aria2 is None:
            return
        ret = aria2.get_active_tasks()
        if ret is not None:
            self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_download)

        ret = aria2.get_waiting_tasks()
        if ret is not None:
            self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_waiting)

        ret = aria2.get_stopped_tasks()
        if ret is not None:
            self.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_stopped)
