#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *
import gl


class UITaskWaiting(UITask):
    def __init__(self, qss='qss/UITaskWaiting.qss'):
        super(UITaskWaiting, self).__init__(qss)
        self.setObjectName('TaskWaiting')

        self.command_recover = QPushButton()
        self.command_recover.setFixedWidth(32)
        with open('./qss/command_button.qss', 'r') as f:
            self.command_recover.setStyleSheet(f.read())
        pm = QPixmap('./icons/recove.png')
        self.command_recover.setIcon(QIcon(pm))
        self.command_recover.setToolTip("恢复下载")
        self.command_recover.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_recover)

        self.progress = QProgressBar()
        self.progress.setFormat("")
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.layout.addWidget(self.progress)

    def set_task(self, task):
        super(UITaskWaiting, self).set_task(task)
        total_len = int(task["totalLength"])
        if total_len == 0:
            total_len = 1
        val = int(task["completedLength"]) * 1000 / total_len
        self.progress.setValue(int(val))

    def _command(self):
        super(UITaskWaiting, self)._command()

        sender = self.sender()
        if sender is self.command_recover:
            aria2 = gl.get_value('aria2')
            aria2.unpause(self.task['gid'])
