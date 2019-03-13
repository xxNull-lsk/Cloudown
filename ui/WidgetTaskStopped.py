#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *


class UITaskStopped(UITask):
    def __init__(self):
        super(UITaskStopped, self).__init__()
        self.setObjectName('TaskStopped')
        self.update_ui()

    def update_ui(self):
        self.command_open.setToolTip(self.tr('Open folder of the file'))
        self.command_delete.setToolTip(self.tr("Delete"))
        self.command_details.setToolTip(self.tr("Details"))
        self.label_file_size.setToolTip(self.tr("File size"))
        self.label_upload_size.setToolTip(self.tr("Upload size"))
