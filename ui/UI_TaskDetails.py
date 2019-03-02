#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import gl


class UiTaskDetails(QWidget):
    def __init__(self, parent):
        super(UiTaskDetails, self).__init__(parent)
