#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *


class UITaskWaiting(UITask):
    def __init__(self, qss='qss/UITaskWaiting.qss'):
        super(UITaskWaiting, self).__init__(qss)
        self.setObjectName('TaskWaiting')

        self.command_recover = QPushButton()
        self.command_recover.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_recover)

        self.progress = QProgressBar()
        self.progress.setFormat("")
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.layout.addWidget(self.progress, 3, 0, 1, 5)

        # TODO: 设置图标
        self.command_recover.setText("恢复")
        self.command_recover.setStatusTip("恢复下载")

    def setData(self, task):
        super(UITaskWaiting, self).setData(task)
        val = int(task["completedLength"]) * 1000 / int(task["totalLength"])
        self.progress.setValue(int(val))

    def _command(self):
        super(UITaskWaiting, self)._command()

        sender = self.sender()
        if sender is self.command_recover:
            QMessageBox.information(self, "TODO", "恢复任务", QMessageBox.Ok)
            # TODO: 恢复任务
            pass
