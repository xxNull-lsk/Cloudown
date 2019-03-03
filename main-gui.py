
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *
import gl
import _thread


class DownloadManager:
    settings = SystemSettings()
    aria2c_exe_name = None

    def __init__(self):
        self.settings.load()
        if self.settings.values['IS_LOCALE']:
            self.aria2c_exe_name = 'aria2c.exe'
            self.settings.values['SERVER_URL'] = 'http://127.0.0.1:6800/jsonrpc'
            _thread.start_new_thread(self.start_aria2, ())
        self.aria2 = Aria2(self.settings.values['SERVER_URL'], self.settings.values['SERVER_TOKEN'])
        gl.set_value("aria2", self.aria2)
        self.app = QApplication(sys.argv)
        self.main_wnd = UiMain('下载管理', self)
        self.t = QTimer()
        self.t.setInterval(1000)

    def start_aria2(self):
        if sys.platform == 'win32':
            app_file = os.path.abspath(os.path.join(self.settings.values['ARIA2'], self.aria2c_exe_name))
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            command = app_file
            for p in self.settings.values['PARAMS']:
                p = p.replace('${START_FOLDER}/', os.path.abspath('./aria2/'))
                p = p.replace('${DOWNLOAD}', download_path)
                command = command + ' ' + p
            command = command + ' --dir="{}"'.format(self.settings.values['DOWNLOAD_DIR'])
            command = command.replace('${START_FOLDER}/', os.path.abspath('./aria2/'))
            command = command.replace('${DOWNLOAD}', download_path)
            os.system(command)
            exit(1)

    def __del__(self):
        self.stop()

    def start(self):
        self.t.timeout.connect(self.task_refresh)
        self.t.start()
        self.main_wnd.show()
        self.task_refresh()
        self.app.exec()

        if self.aria2c_exe_name is not None:
            cmd = 'taskkill /F /IM {}'.format(self.aria2c_exe_name)
            os.system(cmd)

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
