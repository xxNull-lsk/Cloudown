#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTaskActive import *
from ui.WidgetTaskWaiting import UITaskWaiting
from ui.WidgetTaskStopped import UITaskStopped
from ui.UI_Setting import UiSetting


class UiMain(QWidget):
    task_type_all = 0
    task_type_download = 1
    task_type_waiting = 2
    task_type_stopped = 3
    task_downloading = []
    task_waiting = []
    task_stopped = []

    def __init__(self, name, qss):
        super(UiMain, self).__init__()
        self.setObjectName('LeftTabWidget')
        self.resize(800, 600)
        
        self.setWindowTitle(name)
        with open(qss, 'r') as f:   # 导入QListWidget的qss样式
            self.list_style = f.read()

        self.main_layout = QHBoxLayout(self, spacing=0)     # 窗口的整体布局
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.left_layout = QVBoxLayout()     # 左侧选项列表
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.left_layout.setSpacing(10)
        self.left_layout.setContentsMargins(0, 0, 5, 0)
        self.main_layout.addLayout(self.left_layout)

        self.middle_widget = QListWidget()     # 中间选项列表
        self.middle_widget.setStyleSheet(self.list_style)
        self.main_layout.addWidget(self.middle_widget)

        self.right_widget = QListWidget()

        self.main_layout.addWidget(self.right_widget)

        self._setup_ui()

    def _setup_ui(self):
        self.middle_widget.currentRowChanged.connect(self.task_type_changed)   # list和右侧窗口的index对应绑定
        self.middle_widget.setFrameShape(QListWidget.NoFrame)    # 去掉边框
        self.middle_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.middle_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        list_str = ['添加', '配置']
        self.button_new_task = QPushButton(list_str[0])
        self.button_new_task.clicked.connect(self.add_task)
        self.left_layout.addWidget(self.button_new_task)
        self.button_setting = QPushButton(list_str[1])
        self.button_setting.clicked.connect(self.change_setting)
        self.left_layout.addWidget(self.button_setting)

        list_str = ['全部', '下载中', '等待中', '已完成']
        for i in range(len(list_str)):
            self.item = QListWidgetItem(list_str[i], self.middle_widget)
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)

        self.middle_widget.setCurrentRow(0)

    def set_tasks(self, tasks, task_type):
        if task_type == self.task_type_download:
            self.task_downloading = tasks
        elif task_type == self.task_type_waiting:
            self.task_waiting = tasks
        elif task_type == self.task_type_stopped:
            self.task_stopped = tasks

        self.task_type_changed(self.middle_widget.currentIndex())

    def _set_tasks(self, tasks, ui_type):
        for task in tasks:
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.right_widget.width(), 120))
            self.right_widget.addItem(item)
            t = ui_type()
            t.setData(task)
            self.right_widget.setItemWidget(item, t)

    def task_type_changed(self, i):
        self.right_widget.clear()
        if i == self.task_type_all:
            self._set_tasks(self.task_downloading, UITaskActive)
            self._set_tasks(self.task_waiting, UITaskWaiting)
            self._set_tasks(self.task_stopped, UITaskStopped)

        elif i == self.task_type_download:
            self._set_tasks(self.task_downloading, UITaskActive)

        elif i == self.task_type_waiting:
            self._set_tasks(self.task_waiting, UITaskWaiting)

        elif i == self.task_type_stopped:
            self._set_tasks(self.task_stopped, UITaskStopped)

    def add_task(self):
        pass

    def change_setting(self):
        ui = UiSetting(self)
        ui.show()
