#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *


class UITaskStopped(UITask):
    def __init__(self, qss='qss/UITaskStopped.qss'):
        super(UITaskStopped, self).__init__(qss)
        self.setObjectName('TaskStopped')
