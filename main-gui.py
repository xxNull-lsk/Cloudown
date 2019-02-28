
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *

# SERVER_URL = 'http://192.168.2.100:6800/jsonrpc'


class DownloadManager:
    settings = SystemSettings()

    def __init__(self):
        self.aria2 = Aria2(self.settings.SERVER_URL, self.settings.SERVER_TOKEN)
        self.app = QApplication(sys.argv)
        self.main_wnd = UiMain('下载管理', 'qss/ui_main.qss')
        self.t = QTimer()
        self.t.setInterval(1000)

    def __del__(self):
        self.stop()

    def start(self):
        self.t.timeout.connect(self.task_refresh)
        # self.t.start()
        self.main_wnd.show()
        self.task_refresh()
        self.app.exec()

    def stop(self):
        pass

    def task_refresh(self):
        ret = self.aria2.get_active_tasks()
        if ret is not None:
            self.main_wnd.set_tasks(ret["result"], UiMain.task_type_download)

        ret = self.aria2.get_waiting_tasks()
        if ret is not None:
            self.main_wnd.set_tasks(ret["result"], UiMain.task_type_waiting)

        ret = self.aria2.get_stopped_tasks()
        if ret is not None:
            self.main_wnd.set_tasks(ret["result"], UiMain.task_type_stopped)


def main():
    dm = DownloadManager()
    dm.start()


if __name__ == '__main__':
    main()
