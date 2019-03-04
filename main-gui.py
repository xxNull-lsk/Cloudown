
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *
import gl
import _thread


class DownloadManager:
    settings = SystemSettings()
    aria2c_exe_name = None
    aria2 = None

    def __init__(self):
        gl.set_value("dm", self)
        gl.set_value("settings", self.settings)
        gl.set_value("aria2", self.aria2)
        self.settings.load()
        self.init_aria2()
        self.app = QApplication(sys.argv)
        self.main_wnd = UiMain('下载管理', self)

    def start_locale_aria2(self):
        if sys.platform == 'win32':
            app_file = os.path.abspath(os.path.join(self.settings.values['LOCALE']['ARIA2'], self.aria2c_exe_name))
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            command = app_file
            for p in self.settings.values['LOCALE']['PARAMS']:
                p = p.replace('${START_FOLDER}/', os.path.abspath('./aria2/'))
                p = p.replace('${DOWNLOAD}', download_path)
                command = command + ' ' + p
            command = command + ' --dir="{}"'.format(self.settings.values['LOCALE']['DOWNLOAD_DIR'])
            command = command.replace('${START_FOLDER}/', os.path.abspath('./aria2/'))
            command = command.replace('${DOWNLOAD}', download_path)
            os.system(command)
            exit(1)

    def stop_local_aria2(self):
        if self.aria2c_exe_name is not None:
            cmd = 'taskkill /F /IM {}'.format(self.aria2c_exe_name)
            os.system(cmd)
            self.aria2c_exe_name = None

    def __del__(self):
        self.stop_local_aria2()
        gl.set_value("dm", None)
        gl.set_value("settings", None)
        gl.set_value("aria2", None)

    def init_aria2(self):
        self.stop_local_aria2()
        if self.settings.values['IS_LOCALE']:
            self.aria2c_exe_name = 'aria2c.exe'
            url = 'http://127.0.0.1:{}/jsonrpc'.format(self.settings.values["LOCALE"]['SERVER_PORT'])
            token = self.settings.values['LOCALE']['SERVER_TOKEN']
            _thread.start_new_thread(self.start_locale_aria2, ())
            time.sleep(1)
        else:
            url = 'http://{}/jsonrpc'.format(self.settings.values["REMOTE"]['SERVER_ADDRESS'])
            token = self.settings.values['REMOTE']['SERVER_TOKEN']
        self.aria2 = Aria2(url, token)
        gl.set_value("aria2", self.aria2)
        try:
            self.aria2.get_version()
        except Exception as err:
            print(err)
            self.aria2 = None

    def start(self):
        self.main_wnd.show()
        self.app.exec()
        self.stop_local_aria2()


def main():
    dm = DownloadManager()
    dm.start()


if __name__ == '__main__':
    gl._init()
    main()
