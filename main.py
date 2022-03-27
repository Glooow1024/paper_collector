# !/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import logging
from PyQt6.QtWidgets import (QWidget, QDialog, QGridLayout, QLabel, QLineEdit, QTextEdit, QFileDialog, QToolTip, QPushButton, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import (QSize, QRect, QObject, pyqtSignal)
from ieee_conference_spider import get_article_info, search_conferenceID


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


class PaperCollector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        #sys.stdout = LogStream(newText=self.onUpdateText)


    def initUI(self):
        """
        Define the UI playout.
        """
        QToolTip.setFont(QFont('Times', 10))

        # input the conference ID and saved file name
        self.conferenceID_label = QLabel('IEEE conference ID: ')
        self.conferenceID_edit = QLineEdit()
        self.conferenceID_button = QPushButton('Search')
        self.conferenceID_button.clicked.connect(search_conferenceID)
        self.saveFile_label = QLabel('Save to: ')
        self.saveFile_edit = QLineEdit()
        self.saveFile_button = QPushButton('Browse')
        self.saveFile_button.clicked.connect(self.get_save_file_name)
        
        # button to start crawing
        self.startCrawling_button = QPushButton('Start')
        self.startCrawling_button.setToolTip('Click and wait for collecting published paper data.')
        self.startCrawling_button.clicked.connect(self.start_collect_paper)
        self.stopCrawling_button = QPushButton('Stop')
        self.stopCrawling_button.setToolTip('Click to stop collecting data.')
        self.stopCrawling_button.clicked.connect(self.stop_collect_paper)

        # print log
        self.process = QTextEdit(readOnly=True)
        self.process.setFont(QFont("Source Code Pro",9))

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.conferenceID_label, 1, 0)
        grid.addWidget(self.conferenceID_edit, 1, 1)
        grid.addWidget(self.conferenceID_button, 1, 2)
        grid.addWidget(self.saveFile_label, 2, 0)
        grid.addWidget(self.saveFile_edit, 2, 1)
        grid.addWidget(self.saveFile_button, 2, 2)
        grid.addWidget(self.startCrawling_button, 3, 0)
        grid.addWidget(self.stopCrawling_button, 3, 2)
        grid.addWidget(self.process, 4, 0, 3, 3)

        self.setLayout(grid)

        self.setGeometry(300, 300, 700, 300)
        self.setWindowTitle('IEEE paper collector (by Glooow)')
        self.show()


    def get_save_file_name(self):
        """
        Retrive the name of csv file to save.
        """
        self.save_file_name = QFileDialog.getSaveFileName(self, '选择保存路径', '', 'csv(*.csv)')   # (file_name, file_type)
        self.saveFile_edit.setText(self.save_file_name[0])
        #self.show_dialog('save to file: ' + self.save_file_name[0])


    def start_collect_paper(self):
        global logger
        #self.show_dialog('start!')
        get_article_info(self.conferenceID_edit.text(), self.saveFile_edit.text(), logger)
        

    def stop_collect_paper(self):
        self.show_dialog('stop!')


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
