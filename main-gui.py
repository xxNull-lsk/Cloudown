
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *
import gl
import _thread
import logging
import logging.config
import subprocess


class DownloadManager:
    settings = SystemSettings()
    app_name = '云下'
    app_version = '0.1'
    aria2c_exe_name = None
    aria2 = None
    main_wnd = None

    def __init__(self):
        logging.config.fileConfig('logging.conf')
        logging.info("========Download manager starting========")
        gl.set_value("dm", self)
        gl.set_value("settings", self.settings)
        gl.set_value("aria2", self.aria2)
        self.settings.load()
        self.init_aria2()
        self.app = QApplication(sys.argv)
        self.main_wnd = UiMain(self.app_name)

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
            logging.info('local aria2 started')
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            else:
                startupinfo = None
            subprocess.Popen(command, startupinfo=startupinfo)
            # os.system(command)
            logging.info('local aria2 stopped')

    def stop_local_aria2(self):
        if self.settings.values["LOCALE"]["KEEP_RUNNING"]:
            return

        if self.aria2 is None:
            return
        try:
            self.aria2.save_session()
        except:
            pass
        if self.aria2c_exe_name is not None:
            while True:
                try:
                    self.aria2.shutdown()
                    time.sleep(1)
                    self.aria2.get_system_status()
                except:
                    break
            logging.info('local aria2 stopped')
            self.aria2c_exe_name = None

    def __del__(self):
        self.stop_local_aria2()

    def init_aria2(self):
        self.stop_local_aria2()
        if self.settings.values['IS_LOCALE']:
            self.aria2c_exe_name = 'aria2c.exe'
            url = 'http://127.0.0.1:{}/jsonrpc'.format(self.settings.values["LOCALE"]['SERVER_PORT'])
            token = self.settings.values['LOCALE']['SERVER_TOKEN']
            try:
                self.aria2 = Aria2(url, token)
                self.aria2.get_system_status()
            except:
                _thread.start_new_thread(self.start_locale_aria2, ())
                time.sleep(1)
            finally:
                self.aria2 = None
        else:
            url = 'http://{}/jsonrpc'.format(self.settings.values["REMOTE"]['SERVER_ADDRESS'])
            token = self.settings.values['REMOTE']['SERVER_TOKEN']
        self.aria2 = Aria2(url, token)
        gl.set_value("aria2", self.aria2)
        try:
            self.aria2.get_version()
        except Exception as err:
            logging.error('Get version failed!{0}'.format(err))
            self.aria2 = None
            gl.set_value('aria2', self.aria2)

    def start(self):
        self.main_wnd.show()
        logging.debug("Download manager started")
        self.app.exec()
        logging.debug("Download manager exiting")
        self.stop_local_aria2()
        logging.info("====Download manager exited====")


def main():
    dm = DownloadManager()
    dm.start()


if __name__ == '__main__':
    gl._init()
    main()
