#!/usr/bin/env python
# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QColor, QPen
from ui.Misc import *
import gl
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
        if self.bitfield is not None:
            c = int(self.bitfield.total_blocks / size.width())
            if c == 0:
                c = 1
            for i in range(0, self.bitfield.total_blocks, c):
                count = 0
                for x in range(i, i + c):
                    if self.bitfield.is_set(i):
                        count = count + 1
                pen = QPen(QColor(34, 139, 34, int(count * 255 / c)), 1, Qt.SolidLine)
                qp.setPen(pen)
                x = int(i * size.width() / self.bitfield.total_blocks)
                if self.bitfield.is_set(i):
                    qp.drawLine(x, 0, x, size.height() - 1)
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawRect(rt)
        qp.end()


class UiTaskDetails(QWidget):
    def __init__(self, parent):
        self.task = None
        super(UiTaskDetails, self).__init__(parent)
        main_layout = QVBoxLayout(self)
        self.button_back = QPushButton("<<返回")
        self.button_back.setFixedWidth(160)
        self.button_back.clicked.connect(self.on_back)
        main_layout.addWidget(self.button_back)
        self.tab = QTabWidget()
        main_layout.addWidget(self.tab)

        self.base_info = QTableWidget()
        self.tab.addTab(self.base_info, "总览")

        blocks_info = QLabel()
        self.col_count = 80
        self.row_count = 50
        blocks_info.setMinimumSize(self.col_count * 14, self.row_count * 14)
        scroll = QScrollArea()
        scroll.setWidget(blocks_info)
        vbox = QHBoxLayout()
        vbox.addWidget(scroll)
        vbox.setSpacing(0)

        blocks = QWidget()
        blocks.setLayout(vbox)
        self.tab.addTab(blocks, "区块")

        self.blocks_layout = QGridLayout()
        self.blocks_layout.setSpacing(1)
        blocks_info.setLayout(self.blocks_layout)

        self.files_info = QTableWidget()
        self.tab.addTab(self.files_info, "文件")

        self.base_info.setColumnCount(2)
        self.base_info.verticalHeader().hide()
        self.base_info.horizontalHeader().hide()
        self.base_info.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.files_info.setColumnCount(4)
        self.files_info.setHorizontalHeaderLabels(["文件", "总计大小", "已完成大小", "进度"])
        self.files_info.verticalHeader().hide()
        self.files_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.t = QTimer()
        self.t.setInterval(1000)
        self.t.timeout.connect(self.task_refresh)

        self.table_peers = QTableWidget()
        heads = ['地址', '状态', '进度', '下载速度', '上传速度']
        self.table_peers.setColumnCount(len(heads))
        self.table_peers.setHorizontalHeaderLabels(heads)
        self.table_peers.verticalHeader().hide()
        self.table_peers.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.bbbbb()

    def task_refresh(self):
        self.t.stop()
        aria2 = gl.get_value('aria2')
        ret = aria2.get_status(self.task['gid'])
        self.set_data(ret['result'])
        self.t.start()

    def set_data(self, task):
        self.task = task
        peer_tab_index = -1
        for i in range(0, self.tab.count()):
            if self.tab.tabText(i) == '连接信息':
                peer_tab_index = i
                break
        if 'bittorrent' not in task:
            if peer_tab_index >= 0:
                self.tab.removeTab(peer_tab_index)
        elif peer_tab_index < 0:
            peer_tab_index = self.tab.addTab(self.table_peers, '连接信息')
        if peer_tab_index >= 0:
            self.init_peers(task)
        self.init_info(task)
        self.init_blocks(task)
        self.init_files(task)
        dm = gl.get_value('dm')
        dm.main_wnd.root_layout.setCurrentIndex(1)
        self.t.start()

    def init_files(self, task):
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
        self.files_info.resizeColumnsToContents()

    def bbbbb(self):
        col_count = self.col_count
        row_count = self.row_count
        with open("./qss/block.qss", 'r') as f:
            qss = f.read()
        self.blocks_ui = {}
        for row in range(0, row_count):
            for col in range(0, col_count):
                index = row * col_count + col
                name = "block_{}".format(index)
                block_item = QPushButton()
                block_item.setObjectName(name)
                block_item.setStyleSheet(qss)
                block_item.setEnabled(False)
                self.blocks_ui[name] = block_item
                self.blocks_layout.addWidget(block_item, row, col)

    def init_blocks(self, task):
        if task is None or 'bitfield' not in task:
            return
        bitfield = task['bitfield']
        num_pieces = int(task['numPieces'])
        col_count = self.col_count
        row_count = self.row_count  # int((total_count + col_count - 1) / col_count / 2)

        layout = self.blocks_layout
        with open("./qss/block.qss", 'r') as f:
            qss = f.read()
        for row in range(0, row_count):
            for col in range(0, col_count):
                index = row * col_count + col
                index_in_bitfield = int(num_pieces * index / (row_count * col_count))
                name = "block_{}".format(index)
                block_item = self.blocks_ui[name]  # layout.findChild(QPushButton, name)
                if block_item is None:
                    block_item = QPushButton()
                    block_item.setObjectName("block_{}".format(index))
                    block_item.setStyleSheet(qss)
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

    def update_peer(self, row, infos, bitfield):
        for i in range(0, len(infos)):
            self.table_peers.setItem(row, i, QTableWidgetItem(infos[i]))
            self.table_peers.setItem(row, i, QTableWidgetItem(infos[i]))
            if i == 1:
                progress = self.table_peers.cellWidget(row, i)
                if progress is None:
                    progress = UiProgress()
                    self.table_peers.setCellWidget(row, i, progress)
                progress.set_mask(bitfield)

    def init_peers(self, task):
        aria2 = gl.get_value('aria2')
        ret = aria2.get_peers(task['gid'])
        peers = ret['result']
        self.table_peers.setRowCount(len(peers) + 1)
        bitfield = BitField(task['bitfield'], int(task['numPieces']))
        infos = [
            '本机',
            '',
            bitfield.finish_percent,
            '{}/s'.format(size2string(task['downloadSpeed'])),
            '{}/s'.format(size2string(task['uploadSpeed']))
        ]
        self.update_peer(0, infos, bitfield)
        for row in range(0, len(peers)):
            p = peers[row]
            row = row + 1
            bitfield = BitField(p['bitfield'])
            infos = [
                p['ip'] + ':' + p['port'],
                '',
                bitfield.finish_percent,
                '{}/s'.format(size2string(p['downloadSpeed'])),
                '{}/s'.format(size2string(p['uploadSpeed']))
            ]
            self.update_peer(row, infos, bitfield)
        self.table_peers.resizeColumnsToContents()

    def init_info(self, task):
        infos = [
            {'k': "gid", 'v': task['gid']},
            {'k': "文件大小", 'v': size2string(task['totalLength'])},
            {'k': "下载目录", 'v': task['dir']},
            {'k': "状态", 'v': task['status']},
            {'k': "连接数", 'v': task['connections']},
            {'k': "下载大小", 'v': size2string(task['completedLength'])},
            {'k': "下载速度", 'v': "{}/s".format(size2string(task['downloadSpeed']))},
            {'k': "上传大小", 'v': size2string(task['uploadLength'])},
            {'k': "上传速度", 'v': "{}/s".format(size2string(task['uploadSpeed']))},
            {'k': "分片数量", 'v': task['numPieces']},
            {'k': "分片大小", 'v': size2string(task['pieceLength'])},
            {'k': "文件数", 'v': "{}".format(len(task['files']))},
        ]
        self.base_info.setRowCount(len(infos))
        for i in range(0, len(infos)):
            self.base_info.setItem(i, 0, QTableWidgetItem(infos[i]['k']))
            self.base_info.setItem(i, 1, QTableWidgetItem(infos[i]['v']))
        self.base_info.resizeColumnsToContents()

        self.base_info.setColumnWidth(1, self.base_info.width() - self.base_info.columnWidth(0))

    def on_back(self):
        dm = gl.get_value('dm')
        self.t.stop()
        dm.main_wnd.root_layout.setCurrentIndex(0)
