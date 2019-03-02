#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *
import time


class UITaskActive(UITask):
    def __init__(self, qss='qss/UITaskActive.qss'):
        super(UITaskActive, self).__init__(qss)
        self.setObjectName('TaskActive')

        self.command_pause = QPushButton("暂停")
        self.command_pause.setToolTip("暂停下载")
        self.command_pause.clicked.connect(self._command)
        self.commands.insertWidget(0, self.command_pause)

        self.label_time = QLabel()
        self.label_time.setToolTip("剩余时间")
        self.layout.addWidget(self.label_time, 2, 3)

        self.label_download_speed = QLabel()
        self.label_download_speed.setToolTip("下载速度")
        self.layout.addWidget(self.label_download_speed, 2, 4)

        self.label_upload_speed = QLabel()
        self.label_upload_speed.setToolTip("上传速度")
        self.layout.addWidget(self.label_upload_speed, 2, 5)

        self.progress = QProgressBar()
        self.progress.setFormat("")
        self.progress.setFixedHeight(3)
        self.progress.setRange(0, 1000)
        self.layout.addWidget(self.progress, 3, 0, 1, 6)

    def setData(self, task):
        super(UITaskActive, self).setData(task)
        completed_length = int(task["completedLength"])
        total_length = int(task["totalLength"])
        if total_length > 0:
            val = int(completed_length * 1000 / total_length)
        else:
            val = 0

        self.progress.setValue(val)
        self.label_file_size.setText("{0} / {1}".format(size2string(completed_length), size2string(total_length)))
        download_speed = int(task['downloadSpeed'])
        remain_time = 0
        if download_speed > 0:
            remain_time = (total_length - completed_length) / download_speed
        if remain_time >= 60 * 60 * 24:
            remain_time = "未知"
        else:
            remain_time = time.strftime('%H:%M:%S', time.localtime(remain_time))
        self.label_time.setText('剩余时间：{}'.format(remain_time))
        self.label_download_speed.setText('下载速度：{}/s'.format(size2string(download_speed)))
        self.label_upload_speed.setText('上传速度：{}/s'.format(size2string(task['uploadSpeed'])))

    def _command(self):
        super(UITaskActive, self)._command()

        sender = self.sender()
        if sender is self.command_pause:
            QMessageBox.information(self, "TODO", "暂停任务", QMessageBox.Ok)
            # TODO: 暂停任务
            pass
