#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *
import gl


class UITaskWaiting(UITask):
    def __init__(self):
        super(UITaskWaiting, self).__init__()
        self.setObjectName('TaskWaiting')

        self.command_unpause = UiCommandButton()
        self.command_unpause.setObjectName('CommandUnpause')
        self.command_unpause.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_unpause)

        self.progress_layout = QHBoxLayout()
        self.layout.addLayout(self.progress_layout)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.progress_layout.addWidget(self.progress)

        self.label_percent = QLabel()
        self.label_percent.setFixedWidth(64)
        self.label_percent.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progress_layout.addWidget(self.label_percent)

        self.update_ui()

    def update_ui(self):
        self.command_unpause.setToolTip(self.tr("Unpause"))
        self.command_open.setToolTip(self.tr('Open folder of the file'))
        self.command_delete.setToolTip(self.tr("Delete"))
        self.command_details.setToolTip(self.tr("Details"))
        self.label_file_size.setToolTip(self.tr("File size"))
        self.label_upload_size.setToolTip(self.tr("Upload size"))

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.command_unpause.animation_show()

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.command_unpause.animation_hide()

    def set_task(self, task):
        super(UITaskWaiting, self).set_task(task)
        completed_length = int(task["completedLength"])
        total_length = int(task["totalLength"])
        if total_length > 0:
            val = int(completed_length * 1000 / total_length)
            percent = '%03.2f%%' % (completed_length * 100.0 / total_length)
        else:
            val = 0
            percent = '%3.2f%%' % 0
        self.label_percent.setText('{0}'.format(percent))
        self.progress.setValue(val)
        file_size = "{0} / {1}".format(size2string(completed_length), size2string(total_length))
        self.label_file_size.setText('{}'.format(file_size))

    def _command(self):
        sender = self.sender()
        if sender is self.command_unpause:
            aria2 = gl.get_value('aria2')
            aria2.unpause(self.task['gid'])
            aria2.save_session()
        else:
            super()._command()
