#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.Misc import *
import gl
import os
import logging
import json


class BitField:
    data = ''
    total_blocks = 0
    finish_blocks = 0
    finish_percent = ''

    def __init__(self, data, block_count=-1):
        self.data = data

        char_count = len(data) - 1
        if block_count > 0:
            char_count = int((block_count + 3) / 4)
        for index in range(0, char_count):
            bit = data[index]
            bit = int(bit, 16)
            for i in range(0, 4):
                self.total_blocks = self.total_blocks + 1
                if (bit & (1 << i)) != 0:
                    self.finish_blocks = self.finish_blocks + 1

        if self.total_blocks > 0:
            self.finish_percent = '%.2f%%' % (self.finish_blocks * 100 / self.total_blocks)
        else:
            self.finish_percent = "0%"

    def is_set(self, index):
        if self.data is None or index >= self.total_blocks:
            return False

        data_index = int(index / 4)
        bit_index = index % 4
        d = self.data[data_index]
        d = int(d, 16)
        if (d & (1 << bit_index)) == 0:
            return False
        return True


class UiProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.bitfield = None
        self.setMinimumWidth(240)

    def set_mask(self, bitfield):
        self.bitfield = bitfield

    def paintEvent(self, e):
        qp = QPainter()
        size = self.size()
        rt = QRect(0, 0, size.width() - 1, size.height() - 1)
        qp.begin(self)
        qp.fillRect(rt, QColor(0xff, 0xff, 0xff))
        if self.bitfield is not None and self.bitfield.total_blocks > 0:
            c = int(size.width() / self.bitfield.total_blocks)
            if c == 0:
                c = 1
            for i in range(0, size.width()):
                count = 0
                index_in_blocks = int(i * self.bitfield.total_blocks / size.width())
                for x in range(index_in_blocks, index_in_blocks + c):
                    if self.bitfield.is_set(x):
                        count = count + 1
                pen = QPen(QColor(34, 139, 34, int(count * 255 / c)), 1, Qt.SolidLine)
                qp.setPen(pen)
                qp.drawLine(i, 0, i, size.height() - 1)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(rt)
        qp.end()


class UiTaskDetails(QWidget):
    tab_title_peers = 'BT客户端'
    tab_title_servers = '服务器列表'
    tab_title_blocks = '区块'
    tab_title_infos = '总览'
    tab_title_files = '文件'
    tab_title_orgdata = '原始数据'
    backup_tasks = []

    def __init__(self, parent):
        self.task = None
        super(UiTaskDetails, self).__init__(parent)
        main_layout = QVBoxLayout(self)
        self.tab = QTabWidget()
        self.tab.tabBar().setObjectName('TaskDetailsTab')
        main_layout.addWidget(self.tab)

        label = QLabel()
        self.tab.addTab(label, '<<返回')

        self.base_info = QTableWidget()
        self.tab.addTab(self.base_info, self.tab_title_infos)
        self.tab.currentChanged.connect(self.on_tab_changed)
        self.tab.tabBarClicked.connect(self.on_tab_clicked)

        blocks_info = QLabel()
        self.col_count = 80
        self.row_count = 50
        blocks_info.setMinimumSize(self.col_count * 14, self.row_count * 14)
        scroll = QScrollArea()
        scroll.setWidget(blocks_info)
        vbox = QHBoxLayout()
        vbox.addWidget(scroll)
        vbox.setSpacing(0)

        self.blocks = QWidget()
        self.blocks.setLayout(vbox)

        self.blocks_layout = QGridLayout()
        self.blocks_layout.setSpacing(1)
        blocks_info.setLayout(self.blocks_layout)

        self.files_info = QTableWidget()
        self.tab.addTab(self.files_info, self.tab_title_files)

        self.base_info.setColumnCount(3)
        self.base_info.verticalHeader().hide()
        self.base_info.horizontalHeader().hide()
        self.base_info.setEditTriggers(QAbstractItemView.NoEditTriggers)

        heads = ["文件", "总计大小", "已完成大小", "进度", '操作']
        self.files_info.setColumnCount(len(heads))
        self.files_info.setHorizontalHeaderLabels(heads)
        self.files_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t = QTimer()
        self.t.setInterval(1000)
        self.t.timeout.connect(self._refresh_task)

        self.table_peers = QTableWidget()
        heads = ['地址', '状态', '进度', '下载速度', '下载状态', '上传速度', '上传状态']
        self.table_peers.setColumnCount(len(heads))
        self.table_peers.setHorizontalHeaderLabels(heads)
        self.table_peers.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.edit_origins = QTextEdit()
        self.edit_origins.setReadOnly(True)
        self.tab.addTab(self.edit_origins, self.tab_title_orgdata)

        self.table_servers = QTableWidget()
        self.table_servers.setColumnCount(1)
        self.table_servers.horizontalHeader().hide()
        self.table_servers.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self._init_blocks_ui()
        self.tab.setCurrentIndex(1)

    def _init_blocks_ui(self):
        col_count = self.col_count
        row_count = self.row_count
        self.blocks_ui = {}
        for row in range(0, row_count):
            for col in range(0, col_count):
                index = row * col_count + col
                name = "block_{}".format(index)
                block_item = QPushButton()
                block_item.setObjectName('BlockItem')
                block_item.setEnabled(False)
                self.blocks_ui[name] = block_item
                self.blocks_layout.addWidget(block_item, row, col)

    def _refresh_task(self):
        aria2 = gl.get_value('aria2')
        if aria2 is None:
            return
        try:
            ret = aria2.get_status(self.task['gid'])
            self.update_task(ret['result'])
        except Exception as err:
            logging.error('_refresh_task: {}'.format(err))

    def update_task(self, task):
        self.t.stop()
        if task is None:
            return
        # 查看原始数据时不刷新，以防止查过时发生变化，无法分析。
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_orgdata:
            self.edit_origins.setText(json.dumps(task, indent=4))
        if self.tab.currentIndex() == 0:
            self.tab.setCurrentIndex(1)
        self.task = task
        peer_tab_index = -1
        server_tab_index = -1
        block_tab_index = -1
        for i in range(0, self.tab.count()):
            if self.tab.tabText(i) == self.tab_title_peers:
                peer_tab_index = i
            elif self.tab.tabText(i) == self.tab_title_servers:
                server_tab_index = i
            elif self.tab.tabText(i) == self.tab_title_blocks:
                block_tab_index = i

        need_server_tab = False
        if 'bittorrent' in task and 'announceList' in task:
            need_server_tab = True

        if server_tab_index >= 0 and not need_server_tab:
            self.tab.removeTab(server_tab_index)
            server_tab_index = -1
        if server_tab_index < 0 and need_server_tab:
            server_tab_index = self.tab.addTab(self.table_servers, self.tab_title_servers)

        need_peers_tab = False
        if 'bittorrent' in task and task['status'] == 'active':
            need_peers_tab = True

        if peer_tab_index >= 0 and not need_peers_tab:
            self.tab.removeTab(peer_tab_index)
            peer_tab_index = -1

        if peer_tab_index < 0 and need_peers_tab:
            peer_tab_index = self.tab.addTab(self.table_peers, self.tab_title_peers)

        if 'bitfield' not in task:
            if block_tab_index >= 0:
                self.tab.removeTab(block_tab_index)
                block_tab_index = -1
        else:
            if block_tab_index < 0:
                block_tab_index = self.tab.addTab(self.blocks, self.tab_title_blocks)

        if peer_tab_index >= 0:
            try:
                aria2 = gl.get_value('aria2')
                ret = aria2.get_peers(task['gid'])
                peers = ret['result']
                self._update_peers(task, peers)
            except:
                pass
        else:
            peers = None

        if server_tab_index >= 0:
            self._update_servers(task)

        if block_tab_index >= 0:
            self._update_blocks(task)

        self._update_base_info(task, peers)
        self._update_files(task)
        if task['status'] == 'active' and not self.t.isActive():
            self.t.start()

    def _update_servers(self, task):
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_servers:
            return
        if 'bittorrent' not in task:
            return
        if 'announceList' not in task['bittorrent']:
            return
        announce_list = task['bittorrent']['announceList']
        self.table_servers.setRowCount(len(announce_list))
        for i in range(0, len(announce_list)):
            item = announce_list[i][0]
            self.table_servers.setItem(i, 0, QTableWidgetItem(str(item)))
        self.table_servers.resizeColumnsToContents()

    def _update_files(self, task):
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_files:
            return
        files = task['files']
        self.files_info.setRowCount(len(files))
        for i in range(0, len(files)):
            self.files_info.setItem(i, 0, QTableWidgetItem(files[i]['path']))
            length = int(files[i]['length'])
            completed_length = int(files[i]['completedLength'])
            self.files_info.setItem(i, 1, QTableWidgetItem(size2string(length)))
            self.files_info.setItem(i, 2, QTableWidgetItem(size2string(completed_length)))
            if length > 0:
                precent = "%.2f%%" % (completed_length * 100 / length)
            else:
                precent = '0%'
            self.files_info.setItem(i, 3, QTableWidgetItem(precent))
            item = QTableWidgetItem('')
            self.files_info.setItem(i, 4, item)

            w = QWidget()
            lay = QHBoxLayout(w)
            lay.setSpacing(0)
            lay.setContentsMargins(0, 0, 0, 0)
            button_open = QPushButton()
            lay.addWidget(button_open, Qt.AlignCenter)
            button_open.setObjectName('ButtonOpenFile')
            button_open.setWhatsThis(files[i]['path'])
            button_open.setToolTip("打开文件所在目录")
            button_open.clicked.connect(self._on_open_file)
            self.files_info.setCellWidget(i, 4, w)
            self.files_info.setRowHeight(i, 36)

        self.files_info.resizeColumnsToContents()

    def _on_open_file(self):
        file = self.sender().whatsThis()
        dm = gl.get_value('dm')
        if not dm.settings.values['IS_LOCALE']:
            QMessageBox.warning(self, '警告', '当前是远程服务器模式，无法打开文件所在目录。', QMessageBox.Ok)
            return

        os.system('explorer /e,/select,{}'.format(os.path.abspath(file)))

    def _update_blocks(self, task):
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_blocks:
            return
        if task is None or 'bitfield' not in task:
            return
        bitfield = task['bitfield']
        num_pieces = int(task['numPieces'])
        col_count = self.col_count
        row_count = self.row_count  # int((total_count + col_count - 1) / col_count / 2)

        layout = self.blocks_layout
        for row in range(0, row_count):
            for col in range(0, col_count):
                index = row * col_count + col
                index_in_bitfield = int(num_pieces * index / (row_count * col_count))
                name = "block_{}".format(index)
                block_item = self.blocks_ui[name]  # layout.findChild(QPushButton, name)
                if block_item is None:
                    block_item = QPushButton()
                    block_item.setObjectName('BlockItem')
                    layout.addWidget(block_item, row, col)

                byte_off = int(index_in_bitfield / 4)
                if byte_off >= len(bitfield):
                    continue
                bit = bitfield[byte_off]
                bit = int(bit, 16)
                bit_off = 3 - (index_in_bitfield % 4)
                if (bit & (1 << bit_off)) != 0:
                    block_item.setEnabled(True)
                else:
                    block_item.setEnabled(False)

    def _update_peer(self, row, infos, bitfield):
        for i in range(0, len(infos)):
            self.table_peers.setItem(row, i, QTableWidgetItem(infos[i]))
            self.table_peers.setItem(row, i, QTableWidgetItem(infos[i]))
            self.table_peers.setItem(row, i, QTableWidgetItem(infos[i]))
            if i == 1:
                progress = self.table_peers.cellWidget(row, i)
                if progress is None:
                    progress = UiProgress()
                    self.table_peers.setCellWidget(row, i, progress)
                progress.set_mask(bitfield)

    def _update_peers(self, task, peers):
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_peers:
            return
        self.table_peers.setRowCount(len(peers) + 1)
        if 'bitfield' in task:
            bitfield = BitField(task['bitfield'], int(task['numPieces']))
        else:
            bitfield = BitField('', 0)
        infos = [
            '本机',
            '',
            bitfield.finish_percent,
            '{}/s'.format(size2string(task['downloadSpeed'])),
            '',
            '{}/s'.format(size2string(task['uploadSpeed'])),
            ''
        ]
        self._update_peer(0, infos, bitfield)
        for row in range(0, len(peers)):
            p = peers[row]
            row = row + 1
            bitfield = BitField(p['bitfield'])
            infos = [
                p['ip'] + ':' + p['port'],
                '',
                bitfield.finish_percent,
                '{}/s'.format(size2string(p['downloadSpeed'])),
                choking2string(p['peerChoking']),
                '{}/s'.format(size2string(p['uploadSpeed'])),
                choking2string(p['amChoking'])
            ]
            self._update_peer(row, infos, bitfield)
        width = 0
        for i in range(0, self.table_peers.columnCount()):
            if i == 1:
                continue
            self.table_peers.resizeColumnToContents(i)
            width = width + self.table_peers.columnWidth(i)
        self.table_peers.setColumnWidth(1, self.table_peers.width() - width - self.table_peers.columnCount() * 4 - 25)

    def _update_base_info(self, task, peers):
        if self.tab.tabText(self.tab.currentIndex()) != self.tab_title_infos:
            return
        infos = [
            {'k': "gid", 'v': task['gid']},
            {'k': "下载目录", 'v': task['dir']},
            {'k': "状态", 'v': task['status']},
            {'k': "连接数", 'v': task['connections']},
            {'k': "文件大小", 'v': size2string(task['totalLength'])},
            {'k': "下载大小", 'v': size2string(task['completedLength'])},
            {'k': "下载速度", 'v': "{}/s".format(size2string(task['downloadSpeed']))},
            {'k': "上传大小", 'v': size2string(task['uploadLength'])},
            {'k': "上传速度", 'v': "{}/s".format(size2string(task['uploadSpeed']))},
            {'k': "分片数量", 'v': task['numPieces']},
            {'k': "分片大小", 'v': size2string(task['pieceLength'])},
            {'k': "文件数", 'v': "{}".format(len(task['files']))},
        ]
        if 'numSeeders' in task:
            infos.append({'k': '发送者数量', 'v': task['numSeeders']})
            if peers is not None:
                health = 0
                for p in peers:
                    if 'bitfield' not in p:
                        continue
                    bit = BitField(p['bitfield'])
                    if int(bit.total_blocks) == 0:
                        continue
                    health = health + int(bit.finish_blocks) * 100 / int(bit.total_blocks)
                infos.append({'k': '健康度', 'v': '%.2f%%' % health})
        if 'following' in task:
            infos.append({'k': '父任务', 'v': task['following']})
        if 'followedBy' in task:
            for f in task['followedBy']:
                infos.append({'k': '子任务', 'v': f})
        if 'infoHash' in task:
            infos.append({'k': 'Hash', 'v': task['infoHash']})
        self.base_info.setRowCount(len(infos))
        for i in range(0, len(infos)):
            self.base_info.setItem(i, 0, QTableWidgetItem(infos[i]['k']))
            self.base_info.setItem(i, 1, QTableWidgetItem(infos[i]['v']))
            if infos[i]['k'] in ('父任务', '子任务'):
                self.base_info.setItem(i, 2, QTableWidgetItem(''))
                button_goto = QPushButton('查看')
                button_goto.setWhatsThis(infos[i]['v'])
                button_goto.clicked.connect(self.on_button_goto)
                self.base_info.setCellWidget(i, 2, button_goto)
            else:
                self.base_info.removeCellWidget(i, 2)

        width = 0
        for i in range(0, self.base_info.columnCount()):
            if i == 1:
                continue
            self.base_info.resizeColumnToContents(i)
            width = width + self.base_info.columnWidth(i)
        self.base_info.setColumnWidth(1, self.base_info.width() - width - self.base_info.columnCount() * 4 - 25)

    def on_button_goto(self):
        sender = self.sender()
        self.backup_tasks.append(self.task['gid'])
        self._goto_task(sender.whatsThis())

    def _goto_task(self, gid):
        if len(self.backup_tasks) > 0:
            self.tab.setTabText(0, '<<返回 ({})'.format(len(self.backup_tasks)))
        else:
            self.tab.setTabText(0, '<<返回')
        aria2 = gl.get_value('aria2')
        ret = aria2.get_status(gid)
        self.update_task(ret['result'])

    def on_back(self):
        task_count = len(self.backup_tasks)
        if task_count == 0:
            dm = gl.get_value('dm')
            self.t.stop()
            dm.main_wnd.show_normal()
            return
        last = self.backup_tasks[task_count - 1]
        self.backup_tasks.pop(task_count - 1)
        self._goto_task(last)

    def on_tab_clicked(self, index):
        if index == 0:
            self.on_back()

    def on_tab_changed(self, index):
        self.update_task(self.task)

