
import sys
from ui.UI_Main import *
from ui.UI_Setting import *
from aria2 import *
import gl
import _thread
import logging
import logging.config
import subprocess
import locale


class DownloadManager:
    settings = SystemSettings()
    app_name = 'Cloudown'
    app_version = '0.3'
    app_url = 'https://github.com/xxNull-lsk/Cloudown'
    aria2c_process = None
    aria2 = None
    main_wnd = None

    def __init__(self):
        logging.config.fileConfig(translate_macro('${DATA_PATH}/logging.conf'))
        logging.info("========Download manager starting========")
        gl.set_value("dm", self)
        gl.set_value("aria2", self.aria2)
        self.settings.load()
        gl.set_value("settings", self.settings)
        self.app = QApplication(sys.argv)
        self.init_aria2()

        index = self.settings.values['LANGUAGE']
        if index == 0:
            filename = locale.getdefaultlocale()[0]
        else:
            filename = self.settings.values['LANGUAGES'][index]['FILE_NAME']
        trans = QTranslator()
        if trans.load(os.path.join('languages', filename)):
            gl.set_value('language', trans)
            self.app.installTranslator(trans)

        self.main_wnd = UiMain()

    def start_local_aria2(self):
        command = os.path.abspath(translate_macro(self.settings.values['LOCALE']['ARIA2']))
        for p in self.settings.values['LOCALE']['PARAMS']:
            command = command + ' ' + translate_macro(p)
        down_path = translate_macro(self.settings.values['LOCALE']['DOWNLOAD_DIR'])
        command = command + '' + ' --dir="{}"'.format(down_path)
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        elif sys.platform == 'linux':
            pass
        self.aria2c_process = subprocess.Popen(command, startupinfo=startupinfo, shell=True)
        logging.info('local aria2 started(PID={0})'.format(self.aria2c_process.pid))
        pid = self.aria2c_process.pid
        self.aria2c_process.wait()
        returncode = -1
        if self.aria2c_process is not None:
            returncode = self.aria2c_process.returncode
        logging.info('local aria2 stopped(PID={0}, EXIT={1})', pid, returncode)

    def stop_local_aria2(self):
        if self.settings.values["LOCALE"]["KEEP_RUNNING"]:
            return

        if self.aria2 is None:
            return
        try:
            self.aria2.save_session()
        except:
            pass

        if self.aria2c_process is not None:
            while True:
                try:
                    self.aria2.shutdown()
                    time.sleep(1)
                    self.aria2.get_system_status()
                except:
                    break
            self.aria2c_process.kill()
            logging.info('local aria2 stopped(PID={0}, EXIT={1})'.format(self.aria2c_process.pid, self.aria2c_process.returncode))
            self.aria2c_process = None

    def __del__(self):
        self.stop_local_aria2()

    def init_aria2(self):
        self.stop_local_aria2()
        if self.settings.values['IS_LOCALE']:
            url = 'http://127.0.0.1:{}/jsonrpc'.format(self.settings.values["LOCALE"]['SERVER_PORT'])
            token = self.settings.values['LOCALE']['SERVER_TOKEN']
            try:
                self.aria2 = Aria2(url, token)
                self.aria2.get_system_status()
            except:
                _thread.start_new_thread(self.start_local_aria2, ())
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
