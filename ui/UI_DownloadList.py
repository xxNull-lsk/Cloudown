#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTaskActive import *
from ui.WidgetTaskWaiting import UITaskWaiting
from ui.WidgetTaskStopped import UITaskStopped
import json


class SortBySize(QSortFilterProxyModel):
    def __init__(self):
        super(SortBySize, self).__init__()

    def lessThan(self, left, right):
        print(left, right)


class UiDownloadList(QWidget):
    task_type_all = 0
    task_type_download = 1
    task_type_waiting = 2
    task_type_stopped = 3
    task_downloading = []
    task_waiting = []
    task_stopped = []
    menu = None
    sort_type = 'status'

    def __init__(self, parent):
        super(UiDownloadList, self).__init__(parent)
        self.setObjectName('UiDownloadList')

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QListWidget()
        self.left_widget.setObjectName('DownloadTypeList')
        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QListWidget()
        self.right_widget.setObjectName("DownloadTaskList")

        self.main_layout.addWidget(self.right_widget)
        gl.signals.value_changed.connect(self._value_changed)

        self._setup_ui()

    def _value_changed(self, v):
        if v['name'] == 'language':
            self.update_ui()
        elif v['name'] == 'skin':
            self.update_ui(v['new'])

    def _setup_ui(self):
        self.left_widget.currentRowChanged.connect(self.task_type_changed)
        self.left_widget.setFrameShape(QListWidget.NoFrame)
        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.right_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.right_widget.customContextMenuRequested.connect(self.show_menu)

        list_str = [self.tr('All'), self.tr('Downloading'), self.tr('Waiting'), self.tr('Stopped')]
        for i in range(len(list_str)):
            item = QListWidgetItem(list_str[i], self.left_widget)
            item.setSizeHint(QSize(30, 60))
            item.setTextAlignment(Qt.AlignCenter)

        self.left_widget.setCurrentRow(1)

    def show_menu(self, pos):
        self.menu.exec_(QCursor.pos())

    def update_ui(self, skin=None):
        list_str = [self.tr('All'), self.tr('Downloading'), self.tr('Waiting'), self.tr('Stopped')]
        for i in range(0, self.left_widget.count()):
            item = self.left_widget.item(i)
            item.setText(list_str[i])

    def set_tasks(self, tasks, task_type):
        if task_type == self.task_type_download:
            self.task_downloading = tasks
        elif task_type == self.task_type_waiting:
            self.task_waiting = tasks
        elif task_type == self.task_type_stopped:
            self.task_stopped = tasks

        self.task_type_changed(self.left_widget.currentRow())

    def find_task(self, task):
        for r in self.right_widget.findChildren((UITaskActive, UITaskWaiting, UITaskStopped)):
            if r.task['gid'] == task['gid']:
                return r
        return None

    @staticmethod
    def find_task_in_list(r, tasks):
        for t in tasks:
            if r.task['gid'] == t['gid']:
                return True
        return False

    def _set_tasks(self, tasks):
        last_active = 0
        for i in range(self.right_widget.count() - 1, -1, -1):
            item = self.right_widget.item(i)
            if item is None:
                continue
            ui_task = self.right_widget.itemWidget(item)
            if ui_task is None:
                continue
            if ui_task.task['status'] == 'active' and last_active == 0:
                last_active = i
            if not self.find_task_in_list(ui_task, tasks):
                self.right_widget.removeItemWidget(item)
                self.right_widget.takeItem(self.right_widget.row(item))

        for task in tasks:
            item = self.find_task(task)
            if item is None:
                item = QListWidgetItem()
                item.setSizeHint(QSize(self.right_widget.width(), 96))
                if task['status'] == 'active' and self.sort_type == 'status':
                    self.right_widget.insertItem(last_active, item)
                    last_active = last_active + 1
                else:
                    self.right_widget.addItem(item)
                t = None
                if task['status'] == 'active':
                    t = UITaskActive()
                elif task['status'] in ('waiting', 'paused'):
                    t = UITaskWaiting()
                else:
                    t = UITaskStopped()
                t.set_task(task)
                self.right_widget.setItemWidget(item, t)
            else:
                item.set_task(task)
                pass

    def task_type_changed(self, i):
        if i == self.task_type_all:
            tasks = self.task_downloading
            for t in self.task_waiting:
                tasks.append(t)
            for t in self.task_stopped:
                tasks.append(t)
            self._set_tasks(tasks)

        elif i == self.task_type_download:
            self._set_tasks(self.task_downloading)

        elif i == self.task_type_waiting:
            self._set_tasks(self.task_waiting)

        elif i == self.task_type_stopped:
            self._set_tasks(self.task_stopped)
