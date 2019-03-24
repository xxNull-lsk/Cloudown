#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *
import time
import gl


class UITaskActive(UITask):
    def __init__(self):
        super().__init__()
        self.setObjectName('TaskActive')

        self.command_pause = UiCommandButton()
        self.command_pause.setObjectName('CommandPause')
        self.command_pause.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_pause)

        self.label_percent = QLabel()
        self.info_layout.addWidget(self.label_percent)

        self.label_time = QLabel()
        self.info_layout.addWidget(self.label_time)

        self.label_download_speed = QLabel()
        self.info_layout.addWidget(self.label_download_speed)

        self.label_upload_speed = QLabel()
        self.info_layout.addWidget(self.label_upload_speed)

        self.label_connects = QLabel()
        self.info_layout.addWidget(self.label_connects)

        self.progress = QProgressBar()
        self.progress.setFormat("")
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.layout.addWidget(self.progress)
        self.update_ui()

    def update_ui(self):
        self.command_pause.setToolTip(self.tr("Pause"))
        self.label_percent.setToolTip(self.tr("Percent"))
        self.label_time.setToolTip(self.tr("Remain time"))
        self.label_connects.setToolTip(self.tr("Connects"))
        self.label_download_speed.setToolTip(self.tr("Download speed"))
        self.label_upload_speed.setToolTip(self.tr("Upload speed"))

        self.command_open.setToolTip(self.tr('Open folder of the file'))
        self.command_delete.setToolTip(self.tr("Delete"))
        self.command_details.setToolTip(self.tr("Details"))
        self.label_file_size.setToolTip(self.tr("File size"))
        self.label_upload_size.setToolTip(self.tr("Upload size"))

    def enterEvent(self, a0):
        super().enterEvent(a0)
        self.command_pause.animation_show()

    def leaveEvent(self, a0):
        super().leaveEvent(a0)
        self.command_pause.animation_hide()

    def set_task(self, task):
        super().set_task(task)
        completed_length = int(task["completedLength"])
        total_length = int(task["totalLength"])
        if total_length > 0:
            val = int(completed_length * 1000 / total_length)
            percent = '%03.2f%%' % (completed_length * 100.0 / total_length)
        else:
            val = 0
            percent = '%3.2f%%' % 0
        self.label_percent.setText('{:>8}'.format(percent))

        self.progress.setValue(val)
        file_size = "{0} / {1}".format(size2string(completed_length), size2string(total_length))
        self.label_file_size.setText('{:>24}'.format(file_size))
        download_speed = int(task['downloadSpeed'])
        remain_time = 0
        if download_speed > 0:
            remain_time = (total_length - completed_length) / download_speed
        days = remain_time / (60 * 60 * 24)
        if days >= 1:
            remain_time = self.tr("More than {} day(s)").format(int(days))
        else:
            remain_time = time.strftime('%H:%M:%S', time.gmtime(remain_time))
        self.label_time.setText(remain_time)
        self.label_download_speed.setText(self.tr('{:>12}/s').format(size2string(download_speed)))
        if task['uploadSpeed'] != '0':
            self.label_upload_speed.setText(self.tr('{:>12}/s').format(size2string(task['uploadSpeed'])))
        else:
            self.label_upload_speed.setText('')
        if 'numSeeders' in task and 'connections' in task:
            self.label_connects.setText("{}/{}".format(task['numSeeders'], task['connections']))
            self.label_connects.setToolTip(self.tr("Senders: {}  Connects: {}").format(task['numSeeders'], task['connections']))
        elif 'connections' in task:
            self.label_connects.setText("{}".format(task['connections']))
            self.label_connects.setToolTip(self.tr("Connects: {}").format(task['connections']))

    def _command(self):
        sender = self.sender()
        if sender is self.command_pause:
            aria2 = gl.get_value('aria2')
            ret = aria2.pause(self.task['gid'])
            if ret is None:
                # force pause
                aria2.pause(self.task['gid'], True)
            aria2.save_session()
        else:
            super()._command()
