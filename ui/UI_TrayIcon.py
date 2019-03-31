import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui.Misc import *


class UiTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        setting = gl.get_value('settings')
        skin = setting.values['SKIN']

        self.menu = QMenu()
        self.new_task = QAction(text="新建", parent=self, triggered=self.on_new_task)
        pm = QPixmap(get_icon(skin, "new_task"))
        pm = pm.scaled(16, 16, Qt.KeepAspectRatio)
        self.new_task.setIcon(QIcon(pm))
        self.setting = QAction(text="设置", parent=self, triggered=self.on_setting)
        pm = QPixmap(get_icon(skin, "settings"))
        pm = pm.scaled(16, 16, Qt.KeepAspectRatio)
        self.setting.setIcon(QIcon(pm))
        self.quit = QAction("退出", self, triggered=self.on_quit)

        self.menu.addAction(self.new_task)
        self.menu.addAction(self.setting)
        self.menu.addSeparator()
        self.menu.addAction(self.quit)
        self.setContextMenu(self.menu)

        self.activated.connect(self.on_icon_clicked)
        self.messageClicked.connect(self.on_message_clicked)
        pm = QPixmap(get_icon(skin, "download"))
        self.setIcon(QIcon(pm))
        self.icon = self.MessageIcon()

    def on_icon_clicked(self, reason):
        if reason == 2 or reason == 3:
            pw = self.parent()
            if pw.isVisible():
                pw.hide()
            else:
                pw.show()

    def on_message_clicked(self):
        # self.showMessage("提示", "你点了消息", self.icon)
        self.parent().show()
        pass

    def on_new_task(self):
        self.showMessage("测试", "我是消息", self.icon)

    def on_setting(self):
        self.showMessage("测试", "这儿是设置", self.icon)

    def on_quit(self):
        self.setVisible(False)
        qApp.quit()
        sys.exit()
