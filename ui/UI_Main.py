#!/usr/bin/env python
# -*- coding:utf-8 -*-
from ui.UI_DownloadList import *
from ui.UI_Setting import UiSetting
from ui.UI_NewTask import UiNewTask
from ui.UI_TaskDetails import UiTaskDetails
from ui.UI_About import UiAbout
import logging


class ThreadRefreshTask(QThread):
    update = pyqtSignal(int, list, bool)
    update_status = pyqtSignal(dict, bool)
    is_quit = True
    need_update_list = True
    need_update_status = True
    sleep_seconds = 1

    def __init__(self):
        super().__init__()
        self.aria2 = gl.get_value('aria2')
        gl.signals.value_changed.connect(self._on_value_changed)

    def _on_value_changed(self, info):
        if info['name'] == 'setting':
            setting = info['new']
            self.sleep_seconds = setting.values['REFRESH']

    def set_need_update_list(self, need_update_list):
        self.need_update_list = need_update_list

    def set_need_update_status(self, need_update_status):
        self.need_update_status = need_update_status

    def exit(self, return_code=0):
        super().exit(return_code)
        self.is_quit = True

    def start(self, priority=QThread.NormalPriority):
        self.is_quit = False
        self.aria2 = gl.get_value('aria2')
        settings = gl.get_value('settings')
        self.sleep_seconds = settings.values['REFRESH']
        super().start(priority)

    def run(self):
        while not self.is_quit:
            self._refresh_status()
            if not self._refresh_list():
                break
            self.sleep(self.sleep_seconds)

    def _refresh_list(self):
        if not self.need_update_list:
            return True
        try:
            ret = self.aria2.get_active_tasks()
            if ret is not None:
                self.update.emit(UiDownloadList.task_type_download, ret['result'], True)
            ret = self.aria2.get_waiting_tasks()
            if ret is not None:
                self.update.emit(UiDownloadList.task_type_waiting, ret['result'], True)
            ret = self.aria2.get_stopped_tasks()
            if ret is not None:
                self.update.emit(UiDownloadList.task_type_stopped, ret['result'], True)
            return True
        except Exception as err:
            logging.error(str(err))
            self.update.emit(UiDownloadList.task_type_download, [], False)
            return False

    def _refresh_status(self):
        if not self.need_update_status:
            return
        try:
            ret = self.aria2.get_system_status()
            result = ret['result']
            self.update_status.emit(result, True)
        except Exception as err:
            logging.error(str(err))
            self.update_status.emit({}, False)


class UiCommandList(QLabel):
    currentRowChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        top = QVBoxLayout()
        top.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        top.setSpacing(0)
        top.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(top)

        bottom = QVBoxLayout()
        bottom.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        bottom.setSpacing(0)
        bottom.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(bottom)

        self.top_list = QListWidget()
        self.top_list.setFocusPolicy(Qt.NoFocus)
        self.top_list.setObjectName('CommandList')
        self.top_list.setFrameShape(QListWidget.NoFrame)
        self.top_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.top_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.top_list.currentRowChanged.connect(self._top_current_row_changed)
        self.top_list.itemClicked.connect(self._item_clicked)
        top.addWidget(self.top_list)

        self.bottom_list = QListWidget()
        self.bottom_list.setFocusPolicy(Qt.NoFocus)
        self.bottom_list.setObjectName('CommandList')
        self.bottom_list.setFrameShape(QListWidget.NoFrame)
        self.bottom_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bottom_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bottom_list.currentRowChanged.connect(self._bottom_current_row_changed)
        self.bottom_list.itemClicked.connect(self._item_clicked)
        bottom.addWidget(self.bottom_list)

    def add_top_button(self, object_name, text=''):
        item = QListWidgetItem()
        item.setSizeHint(QSize(self.width(), 64))
        self.top_list.addItem(item)
        label = QLabel(text)
        label.setObjectName(object_name)
        self.top_list.setItemWidget(item, label)

    def add_bottom_button(self, object_name, text=''):
        item = QListWidgetItem()
        item.setSizeHint(QSize(self.width(), 64))
        self.bottom_list.addItem(item)
        label = QLabel(text)
        label.setObjectName(object_name)
        self.bottom_list.setItemWidget(item, label)
        self.bottom_list.setFixedHeight(item.sizeHint().height() * self.bottom_list.count())

    def _item_clicked(self, item):
        if self.sender() == self.top_list:
            index = self.top_list.row(item)
            self._top_current_row_changed(index)
        elif self.sender() == self.bottom_list:
            index = self.bottom_list.row(item)
            self._bottom_current_row_changed(index)

    def _bottom_current_row_changed(self, index):
        self.currentRowChanged.emit(index + self.top_list.count())
        if self.top_list.currentItem() is not None:
            self.top_list.currentItem().setSelected(False)

    def _top_current_row_changed(self, index):
        self.currentRowChanged.emit(index)
        if self.bottom_list.currentItem() is not None:
            self.bottom_list.currentItem().setSelected(False)

    def setCurrentRow(self, index):
        if index < self.top_list.count():
            self.top_list.setCurrentRow(index)
            self._top_current_row_changed(index)
        else:
            index = index - self.top_list.count()
            self.bottom_list.setCurrentRow(index)
            self._bottom_current_row_changed(index)


class UiMain(QWidget):
    name = ''

    def __init__(self):
        super().__init__(QDesktopWidget())
        dm = gl.get_value('dm')
        dm.app_name = self.tr('Cloudown')
        self.name = dm.app_name
        self.setObjectName('UiMain')
        setting = gl.get_value('settings')
        with open('./skins/{0}.qss'.format(setting.values['SKIN']), 'r') as f:
            self.setStyleSheet(f.read())
        self.resize(1024, 768)
        self.root_layout = QStackedLayout(self)
        label = QLabel()

        self.main_layout = QHBoxLayout()
        label.setLayout(self.main_layout)
        self.root_layout.addWidget(label)
        self.ui_details = UiTaskDetails(self)
        self.root_layout.addWidget(self.ui_details)
        self.root_layout.setCurrentIndex(0)

        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.left_widget = UiCommandList()
        self.left_widget.setObjectName('CommandList')
        self.left_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.ui_download_list = UiDownloadList(self)
        self.right_widget.addWidget(self.ui_download_list)

        self.ui_new_task = UiNewTask(self)
        self.right_widget.addWidget(self.ui_new_task)

        self.ui_setting = UiSetting(self)
        self.right_widget.addWidget(self.ui_setting)

        self.ui_about = UiAbout(self)
        self.right_widget.addWidget(self.ui_about)

        self.main_layout.addWidget(self.right_widget)

        self.thread_refresh_task = ThreadRefreshTask()

        self._setup_ui()
        self.update_ui()
        # self.ui_download_list.setParent(self)
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.animation.setDuration(500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InCirc)
        self.animation.start()

    def update_ui(self, skin=None):
        dm = gl.get_value('dm')
        dm.app_name = self.tr('Cloudown')
        self.name = dm.app_name
        if skin is None:
            setting = gl.get_value('settings')
            skin = setting.values['SKIN']
        pm = QPixmap(get_icon(skin, "download"))
        self.setWindowIcon(QIcon(pm))
        with open('./skins/{0}.qss'.format(skin), 'r') as f:
            self.setStyleSheet(f.read())

    def _on_value_changed(self, v):
        if v['name'] == 'aria2':
            self.thread_refresh_task.exit()
            self.thread_refresh_task.start()
        elif v['name'] == 'language':
            self.update_ui()
        elif v['name'] == 'skin':
            self.update_ui(v['new'])

    def update_window_title(self, status, is_successed):

        aria2 = gl.get_value('aria2')
        if aria2 is None or not is_successed:
            name = self.name + self.tr('(Server is offline)')
            status = ""
        else:
            dm = gl.get_value('dm')
            if dm.settings.values['IS_LOCALE']:
                name = self.name + self.tr('(Local)')
            else:
                name = self.name + self.tr('(Remote: {0})').format(dm.settings.values['REMOTE']["SERVER_ADDRESS"])

            if status is not None and 'downloadSpeed' in status:
                status = self.tr('Download Speed: {0}/s  Upload Speed: {1}/s').format(
                    size2string(status['downloadSpeed']),
                    size2string(status['uploadSpeed']))
            else:
                status = ""
        super().setWindowTitle(name + ' ' + status)

    def _setup_ui(self):
        gl.signals.value_changed.connect(self._on_value_changed)
        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)
        self.left_widget.currentRowChanged.connect(self.on_changed_page)

        list_name = ['download_list', 'new_task']
        for i in range(0, len(list_name)):
            self.left_widget.add_top_button(list_name[i])

        list_name = ['settings', 'about']
        for i in range(0, len(list_name)):
            self.left_widget.add_bottom_button(list_name[i])

        self.thread_refresh_task.update.connect(self._task_refresh)
        self.thread_refresh_task.update_status.connect(self.update_window_title)
        self.left_widget.setCurrentRow(0)

    def show_details(self, task):
        if self.thread_refresh_task.isRunning():
            self.thread_refresh_task.set_need_update_list(False)
        self.ui_details.update_task(task)
        self.root_layout.setCurrentIndex(1)

    def show_normal(self):
        if not self.thread_refresh_task.isRunning():
            self.thread_refresh_task.start()

        self.thread_refresh_task.set_need_update_list(True)
        self.root_layout.setCurrentIndex(0)

    def show(self):
        super().show()
        self.show_normal()

    def hide(self):
        super().hide()
        self.thread_refresh_task.exit()

    def _task_refresh(self, task_type, tasks, is_successed):
        aria2 = gl.get_value('aria2')
        if aria2 is not None and is_successed:
            try:
                self.ui_download_list.set_tasks(tasks, task_type)
                return
            except Exception as err:
                print('_task_refresh', err)
                logging.error('_refresh_task: {}'.format(err))
        self.thread_refresh_task.exit()
        self.ui_download_list.set_tasks([], UiDownloadList.task_type_download)
        self.ui_download_list.set_tasks([], UiDownloadList.task_type_waiting)
        self.ui_download_list.set_tasks([], UiDownloadList.task_type_stopped)
        message = self.tr("Aria2 server is offline. Do you want to reconnect it?")
        ret = QMessageBox.critical(self, self.tr('Exception'), message, QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            dm = gl.get_value('dm')
            dm.init_aria2()

    def on_changed_page(self, index):
        if index != 0:
            self.thread_refresh_task.set_need_update_list(False)
        else:
            if not self.thread_refresh_task.isRunning():
                self.thread_refresh_task.start()
            self.thread_refresh_task.set_need_update_list(True)
