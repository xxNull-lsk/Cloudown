
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *
import gl


class DownloadManager:
    settings = SystemSettings()

    def __init__(self):
        self.aria2 = Aria2(self.settings.values['SERVER_URL'], self.settings.values['SERVER_TOKEN'])
        gl.set_value("aria2", self.aria2)
        self.app = QApplication(sys.argv)
        self.main_wnd = UiMain('下载管理', self)
        self.t = QTimer()
        self.t.setInterval(1000)

    def __del__(self):
        self.stop()

    def start(self):
        self.t.timeout.connect(self.task_refresh)
        self.t.start()
        self.main_wnd.show()
        self.task_refresh()
        self.app.exec()

    def stop(self):
        pass

    def task_refresh(self):
        ret = self.aria2.get_active_tasks()
        if ret is not None:
            self.main_wnd.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_download)

        ret = self.aria2.get_waiting_tasks()
        if ret is not None:
            self.main_wnd.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_waiting)

        ret = self.aria2.get_stopped_tasks()
        if ret is not None:
            self.main_wnd.ui_download_list.set_tasks(ret["result"], UiDownloadList.task_type_stopped)


def main():
    dm = DownloadManager()
    gl.set_value("dm", dm)
    dm.start()


if __name__ == '__main__':
    gl._init()
    main()
