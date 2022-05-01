# !/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import time
import logging
from PyQt6.QtWidgets import (QWidget, QDialog, QHBoxLayout, QVBoxLayout, QTabWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QFileDialog, QToolTip, QPushButton, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import (QSize, QRect, QObject, pyqtSignal, QThread)
from ieee_conference_spider import IEEESpider


class LogHandler(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def emit(self, record):
        try:
            print(self.format(record))
            self.parent.print_log(self.format(record))
            QApplication.processEvents()
        except Exception:
            self.handleError(record)


class SpiderThread(QObject):
    _spider_finish = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.flag_running = False
        self.ieee_spider = IEEESpider()

    def __del__(self):
        print('>>> __del__')

    def run(self, conference_ID, save_filename, logger):
        self.ieee_spider.flag_running = True
        self.ieee_spider.get_article_info(conference_ID, save_filename, logger)
        self._spider_finish.emit()
        #self.flag_running = False


class PaperCollector(QWidget):
    _start_spider = pyqtSignal(str, str, logging.Logger)

    def __init__(self):
        super().__init__()
        self.initUI()
        #sys.stdout = LogStream(newText=self.onUpdateText)

        self.spiderT = SpiderThread()
        self.thread = QThread(self)
        self.spiderT.moveToThread(self.thread)
        self._start_spider.connect(self.spiderT.run)        # 只能通过信号槽启动线程处理函数
        #self.spiderT._log_info.connect(self.print_log)
        self.spiderT._spider_finish.connect(self.finish_collect_paper)


    def spiderUI(self):
        """
        Define the UI playout of spider page.
        """

        # input the conference ID and saved file name
        self.conferenceID_label = QLabel('IEEE conference ID: ')
        self.conferenceID_edit = QLineEdit()
        self.conferenceID_button = QPushButton('Search')
        self.conferenceID_button.clicked.connect(IEEESpider.search_conferenceID)
        self.saveFile_label = QLabel('Save to: ')
        self.saveFile_edit = QLineEdit()
        self.saveFile_button = QPushButton('Browse')
        self.saveFile_button.clicked.connect(self.get_save_file_name)
        
        # button to start crawing
        self.startCrawling_button = QPushButton('Start')
        self.startCrawling_button.setToolTip('Click and wait for collecting published paper data ^o^')
        self.startCrawling_button.clicked.connect(self.start_collect_paper)
        self.stopCrawling_button = QPushButton('Stop')
        self.stopCrawling_button.setToolTip('Click to stop collecting data ^_^')
        self.stopCrawling_button.clicked.connect(self.stop_collect_paper)

        # print log
        self.process = QTextEdit(readOnly=True)
        self.process.setFont(QFont("Source Code Pro",9))

        self.spider_grid = QGridLayout()
        self.spider_grid.setSpacing(10)

        self.spider_grid.addWidget(self.conferenceID_label, 1, 0)
        self.spider_grid.addWidget(self.conferenceID_edit, 1, 1)
        self.spider_grid.addWidget(self.conferenceID_button, 1, 2)
        self.spider_grid.addWidget(self.saveFile_label, 2, 0)
        self.spider_grid.addWidget(self.saveFile_edit, 2, 1)
        self.spider_grid.addWidget(self.saveFile_button, 2, 2)
        self.spider_grid.addWidget(self.startCrawling_button, 3, 0)
        self.spider_grid.addWidget(self.stopCrawling_button, 3, 2)
        self.spider_grid.addWidget(self.process, 4, 0, 3, 3)

        self.spider_widget = QWidget()
        self.spider_widget.setLayout(self.spider_grid)

    
    def analyzerUI(self):
        """
        Define the UI playout of analyzer page.
        """
        self.btnn = QPushButton('TEST')

        self.analyzer_grid = QGridLayout()
        self.analyzer_grid.setSpacing(10)
        self.analyzer_grid.addWidget(self.btnn, 1, 0)

        self.analyzer_widget = QWidget()
        self.analyzer_widget.setLayout(self.analyzer_grid)


    def reservedUI(self):
        """
        Define the UI playout of analyzer page.
        """
        self.image = QTextEdit(readOnly=True)
        self.image.setFont(QFont("Source Code Pro",9))

        self.reserved_grid = QGridLayout()
        self.reserved_grid.setSpacing(10)
        self.reserved_grid.addWidget(self.image, 1, 0)

        self.reserved_widget = QWidget()
        self.reserved_widget.setLayout(self.reserved_grid)


    def sidebarUI(self):
        """
        Define the UI playout of sidebar.
        """
        self.sidebar_btn_1 = QPushButton('Collector', self)
        self.sidebar_btn_1.clicked.connect(self.sidebar_button_1)
        self.sidebar_btn_2 = QPushButton('Analyzer', self)
        self.sidebar_btn_2.clicked.connect(self.sidebar_button_2)
        self.sidebar_btn_3 = QPushButton('Reserved', self)
        self.sidebar_btn_3.clicked.connect(self.sidebar_button_3)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar_btn_1)
        sidebar_layout.addWidget(self.sidebar_btn_2)
        sidebar_layout.addWidget(self.sidebar_btn_3)
        sidebar_layout.addStretch(5)
        sidebar_layout.setSpacing(20)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(sidebar_layout)


    def sidebar_button_1(self):
        self.right_widget.setCurrentIndex(0)

    def sidebar_button_2(self):
        self.right_widget.setCurrentIndex(1)

    def sidebar_button_3(self):
        self.right_widget.setCurrentIndex(2)


    def initUI(self):
        """
        Define the UI playout.
        https://www.luochang.ink/posts/pyqt5_layout_sidebar/
        """
        QToolTip.setFont(QFont('Times', 10))

        self.sidebarUI()
        self.spiderUI()
        self.analyzerUI()
        self.reservedUI()

        # 多个标签页
        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        self.right_widget.addTab(self.spider_widget, '')
        self.right_widget.addTab(self.analyzer_widget, '')
        self.right_widget.addTab(self.reserved_widget, '')

        self.right_widget.setCurrentIndex(0)
        self.right_widget.setStyleSheet('''QTabBar::tab{width: 0; height: 0; margin: 0; padding: 0; border: none;}''')

        # overall layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)

        self.setLayout(main_layout)

        #self.setLayout(self.sprder_grid)

        self.setGeometry(300, 300, 850, 300)
        self.setWindowTitle('IEEE paper collector (by Glooow)')
        self.show()


    def get_save_file_name(self):
        """
        Retrive the name of csv file to save.
        """
        self.save_file_name = QFileDialog.getSaveFileName(self, '选择保存路径', '', 'csv(*.csv)')   # (file_name, file_type)
        self.saveFile_edit.setText(self.save_file_name[0])


    def start_collect_paper(self):
        if self.thread.isRunning():
            return
        
        self.startCrawling_button.setEnabled(False)
        self.startCrawling_button.setToolTip('I\'m trying very hard to collect papers >_<')
        # 先启动QThread子线程
        #self.spiderT.flag_running = True
        self.thread.start()
        # 发送信号，启动线程处理函数
        # 不能直接调用，否则会导致线程处理函数和主线程是在同一个线程，同样操作不了主界面
        global logger
        self._start_spider.emit(self.conferenceID_edit.text(), self.saveFile_edit.text(), logger)


    def finish_collect_paper(self):
        self.startCrawling_button.setEnabled(True)
        self.startCrawling_button.setToolTip('Click and wait for collecting published paper data ^o^')
        self.spiderT.ieee_spider.flag_running = False
        self.thread.quit()


    def stop_collect_paper(self):
        if not self.thread.isRunning():
            return
        self.spiderT.ieee_spider.flag_running = False
        time.sleep(15)
        self.thread.quit()      # 退出
        #self.thread.wait()      # 回收资源
        #self.show_dialog('stop!')


    def print_log(self, s):
        self.process.append(s)


    def show_dialog(self, info):
        """
        Pop up dialogs for debug.
        """
        hint_dialog = QDialog()
        hint_dialog.setWindowTitle('Hint info')
        #hint_dialog.setWindowModality(PyQt6.QtCore.Qt.NonModal)

        hint_info = QLabel(info, hint_dialog)
        hint_info.adjustSize()
        padding = 20
        max_width = 360
        # set the maximum width
        if hint_info.size().width() > max_width:
            hint_info.setGeometry(QRect(0, 0, max_width, 80))
            hint_info.setWordWrap(True)
        hint_info.move(padding, padding)

        hint_dialog.resize(hint_info.size() + QSize(padding*2, padding*2))
        hint_dialog.exec()


logger = None

def main():
    app = QApplication(sys.argv)
    ex = PaperCollector()

    global logger
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)
    formater = logging.Formatter(fmt="%(asctime)s [%(levelname)s] : %(message)s"
                ,datefmt="%Y/%m/%d %H:%M:%S")
    handler = LogHandler(ex)
    handler.setFormatter(formater)
    logger.addHandler(handler)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
