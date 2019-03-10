#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.WidgetTask import *


class UITaskStopped(UITask):
    def __init__(self):
        super().__init__()
        self.setObjectName('TaskStopped')
