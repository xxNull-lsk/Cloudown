import os
import gl
from PyQt5.QtWidgets import *


def size2string(size_bytes):
    if isinstance(size_bytes, str):
        size_bytes = int(size_bytes)

    if size_bytes < 1024:
        return "%d B" % size_bytes

    curr = size_bytes / 1024.0
    if curr < 1024:
        return "%.2f KB" % curr
    curr = curr / 1024.0
    if curr < 1024:
        return "%.2f MB" % curr
    curr = curr / 1024.0
    return "%.2f GB" % curr


def choking2string(choking):
    if choking == 'true':
        return '阻塞'
    else:
        return '正常'


def rm_dir(path):
    if os.path.isdir(path):
        for f in os.listdir(path):
            rm_dir(os.path.join(path, f))
        os.removedirs(path)
    else:
        os.unlink(path)


def merged_dict(dict1, dict2):
    for v in dict2:
        if isinstance(dict2[v], dict):
            merged_dict(dict1[v], dict2[v])
        else:
            dict1[v] = dict2[v]


def translate_macro(path):
    path = path.replace('${DATA_PATH}', os.path.abspath('./data'))
    path = path.replace('${ARIA2_PATH}', os.path.abspath('./aria2'))
    path = path.replace('${START_PATH}', os.path.abspath('./aria2'))
    path = path.replace('${START_FOLDER}', os.path.abspath('./aria2'))
    home_path = os.path.expanduser('~')
    path = path.replace('${HOME_PATH}', home_path)
    download_path = os.path.join(home_path, 'Downloads')
    path = path.replace('${DOWNLOAD_PATH}', download_path)
    return path


def get_icon(skin, name):
    return "./skins/{0}/{1}.png".format(skin, name)


class UiMessageBox:
    def __init__(self):
        super().__init__()

    @staticmethod
    def tr(text):
        trans = gl.get_value('language')
        ret = trans.translate('UiMessageBox', text)
        if ret is not None and ret != '':
            return ret
        return text

    @staticmethod
    def button_text(msg):
        text = [UiMessageBox.tr("Yes"), UiMessageBox.tr("No"), UiMessageBox.tr("Ok"), UiMessageBox.tr("Cancel")]
        types = [QMessageBox.Yes, QMessageBox.No, QMessageBox.Ok, QMessageBox.Cancel]
        for i in range(0, len(types)):
            if msg.button(types[i]) is not None:
                msg.button(types[i]).setText(text[i])

    @staticmethod
    def question(parent, title, text, buttons=None):
        msg = QMessageBox(QMessageBox.Question, title, text, buttons, parent)
        UiMessageBox.button_text(msg)
        return msg.exec_()

    @staticmethod
    def warning(parent, title, text, buttons=None):
        msg = QMessageBox(QMessageBox.Warning, title, text, buttons, parent)
        UiMessageBox.button_text(msg)
        return msg.exec_()

