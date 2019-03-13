#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *
import gl


class UITaskWaiting(UITask):
    def __init__(self):
        super(UITaskWaiting, self).__init__()
        self.setObjectName('TaskWaiting')

        self.command_unpause = QPushButton()
        self.command_unpause.setObjectName('CommandUnpause')
        self.command_unpause.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_unpause)

        self.progress = QProgressBar()
        self.progress.setFormat("")
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.layout.addWidget(self.progress)
        self.update_ui()

    def update_ui(self):
        self.command_unpause.setToolTip(self.tr("Unpause"))
        self.command_open.setToolTip(self.tr('Open folder of the file'))
        self.command_delete.setToolTip(self.tr("Delete"))
        self.command_details.setToolTip(self.tr("Details"))
        self.label_file_size.setToolTip(self.tr("File size"))
        self.label_upload_size.setToolTip(self.tr("Upload size"))

    def set_task(self, task):
        super(UITaskWaiting, self).set_task(task)
        total_len = int(task["totalLength"])
        if total_len == 0:
            total_len = 1
        val = int(task["completedLength"]) * 1000 / total_len
        self.progress.setValue(int(val))

    def _command(self):
        sender = self.sender()
        if sender is self.command_unpause:
            aria2 = gl.get_value('aria2')
            aria2.unpause(self.task['gid'])
            aria2.save_session()
        else:
            super()._command()
