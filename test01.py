#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
import shiboken6
# グラフ描写用
#import graph

import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from multiprocessing import Process, Queue, pool
import multiprocessing as mp
import datetime
import time
import csv
import os
import configparser
import threading
import pyautogui as pag

# ダウンロードしたライブラリ
import sys
import configparser
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, QObject, Signal, Slot, QThread
import os
import datetime
import csv
import time


# 以下自作ライブラリ
import temp_phidget
import ace_calcu
import rpm_mcp3008
import logger

#cofficient
#config.ini
parser = configparser.SafeConfigParser() # for ini file
parser.read("config.ini") # deployment for ini file
file_path_header = parser.get("header", "file_path_header") # filepath for the result
file_path_csv = parser.get("csv", "file_path_csv") # filepath for the result
channel_list = eval(parser.get("channel", "channel_list"))

# header
with open(file_path_header) as f:
    reader = csv.reader(f)
    for row in reader:
        header = row
f.close()


counter_list = [0]
counter_list1 = [0]
elapsed_time = [datetime.timedelta(0)]


start_time = []
timer_list = []
elapsed_time = []


timer_list1 = []
start_time1 = []
#elapsed_time = [datetime.timedelta(0)]
elapsed_time1 = [datetime.timedelta(0)]

class Timer(QObject):
    """バックグラウンドで処理を行うクラス
    """
    signal_elaps1 = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__is_canceled = False

    def run(self):
        counter = 54000

        if counter_list[0] == 0:
            while not self.__is_canceled:
                self.tt = datetime.datetime.fromtimestamp(counter)
                self.display = self.tt.strftime("%H:%M:%S")
                counter += 1
                counter_list[0] = counter
                self.signal_elaps1.emit([str(self.display)])
                time.sleep(1)

        else:
            while not self.__is_canceled:
                counter = counter_list[0]
                self.tt = datetime.datetime.fromtimestamp(counter)
                self.display = self.tt.strftime("%H:%M:%S")
                counter += 1
                counter_list[0] = counter
                self.signal_elaps1.emit([str(self.display)])
                time.sleep(1)

    def stop(self):
        self.__is_canceled = True


class Worker(QObject):
    """バックグラウンドで処理を行うクラス
    """
    signal_result = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__is_canceled = False

    def run(self):
        counter = 54000

        if counter_list[0] == 0:

            while not self.__is_canceled:
                self.result1 = []

                self.tt = datetime.datetime.fromtimestamp(counter)
                self.time = self.tt.strftime("%H:%M:%S")

                # date from logger.py
                self.result = logger.logger(4, 2, 6)

                self.result1.append(self.time)
                self.result1.append(self.result[1])
                self.signal_result.emit(self.result1)

                counter += 1
                counter_list[0] = counter

                # cycle at 60 sec
                time.sleep(23.9)


        else:
            while not self.__is_canceled:
                self.result1 = []
                counter = counter_list[0]

                self.tt = datetime.datetime.fromtimestamp(counter)
                self.time = self.tt.strftime("%H:%M:%S")

                # date from logger.py
                self.result = logger.logger(4, 2, 6)

                self.result1.append(self.time)
                self.result1.append(self.result[1])
                self.signal_result.emit(self.result1)

                counter += 1
                counter_list[0] = counter

                # cycle at 60 sec
                time.sleep(23.9)

    def stop(self):
        self.__is_canceled = True

class MainWindow(QWidget):
    """メインウィンドウ
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__thread = None

        self.wo01 = QLineEdit("1", self)
        self.wo01.move(20,10)
        self.wo01.resize(400*0.8, 80)
        self.wo01.setPlaceholderText(' 作業用番号') # 透かしで表示
        self.wo01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど

        self.wk01 = QComboBox(self)
        self.wk01.addItem("A")
        self.wk01.addItem("A")
        self.wk01.addItem("A")
        self.wk01.addItem("A")
        self.wk01.move(390,10)
        self.wk01.resize(400*0.8, 80)
        self.wk01.setStyleSheet("color: black; font: 20pt Arial; border-color: white; "
                                "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど

        self.btn01 = QPushButton("計測開始", self)
        self.btn01.move(750, 10)
        self.btn01.resize(400*0.3, 80)
        self.btn01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                 "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど
        self.btn01.clicked.connect(self.__start)


        self.btn02 = QPushButton("計測停止", self)
        self.btn02.move(910, 10)
        self.btn02.resize(400*0.3, 80)
        self.btn02.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                 "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど
        self.btn02.clicked.connect(self.__stop)


        self.label_elapse = QLabel("経過時間", self) # dummy
        self.label_elapse.move(1100, 10)
        self.label_elapse.resize(400*0.8, 80)
        self.label_elapse.setStyleSheet("color: black; font: 20pt Arial") # 文字の大きさなど

        self.label_elapse1 = QLabel("", self) # dummy
        self.label_elapse1.move(1300, 10)
        self.label_elapse1.resize(400*0.8, 80)
        self.label_elapse1.setStyleSheet("color: black; font: 20pt Arial") # 文字の大きさなど


        self.setGeometry(200, 200, 300, 200)

        layout = QGridLayout()

        # label for channels(temp, rpm and acceralation)
        self.label = QLabel("") # dummy

        self.label_temp_ch0 = QLabel("温度(ch0)")
        self.label_temp_ch1 = QLabel("温度(ch1)")
        self.label_temp_ch2 = QLabel("温度(ch2)")

        self.label_rpm_ch0 = QLabel("回転数(ch0)")
        self.label_rpm_ch1 = QLabel("回転数(ch1)")


        self.label_ace_x_ch0 = QLabel("変位x(ch0)")
        self.label_ace_x_ch1 = QLabel("変位x(ch1)")
        self.label_ace_x_ch2 = QLabel("変位x(ch2)")
        self.label_ace_x_ch3 = QLabel("変位x(ch3)")
        self.label_ace_x_ch4 = QLabel("変位x(ch4)")

        self.label_ace_y_ch0 = QLabel("変位y(ch0)")
        self.label_ace_y_ch1 = QLabel("変位y(ch1)")
        self.label_ace_y_ch2 = QLabel("変位y(ch2)")
        self.label_ace_y_ch3 = QLabel("変位y(ch3)")
        self.label_ace_y_ch4 = QLabel("変位y(ch4)")

        self.label_ace_z_ch0 = QLabel("変位z(ch0)")
        self.label_ace_z_ch1 = QLabel("変位z(ch1)")
        self.label_ace_z_ch2 = QLabel("変位z(ch2)")
        self.label_ace_z_ch3 = QLabel("変位z(ch3)")
        self.label_ace_z_ch4 = QLabel("変位z(ch4)")

        # position
        layout.addWidget(self.label, 0, 0) # dummy

        layout.addWidget(self.label_temp_ch0, 1, 0)
        layout.addWidget(self.label_temp_ch1, 2, 0)
        layout.addWidget(self.label_temp_ch2, 3, 0)

        layout.addWidget(self.label_rpm_ch0, 4, 0)
        layout.addWidget(self.label_rpm_ch1, 5, 0)

        layout.addWidget(self.label_ace_x_ch0, 1, 2)
        layout.addWidget(self.label_ace_x_ch1, 2, 2)
        layout.addWidget(self.label_ace_x_ch2, 3, 2)
        layout.addWidget(self.label_ace_x_ch3, 4, 2)
        layout.addWidget(self.label_ace_x_ch4, 5, 2)

        layout.addWidget(self.label_ace_y_ch0, 1, 4)
        layout.addWidget(self.label_ace_y_ch1, 2, 4)
        layout.addWidget(self.label_ace_y_ch2, 3, 4)
        layout.addWidget(self.label_ace_y_ch3, 4, 4)
        layout.addWidget(self.label_ace_y_ch4, 5, 4)

        layout.addWidget(self.label_ace_z_ch0, 1, 6)
        layout.addWidget(self.label_ace_z_ch1, 2, 6)
        layout.addWidget(self.label_ace_z_ch2, 3, 6)
        layout.addWidget(self.label_ace_z_ch3, 4, 6)
        layout.addWidget(self.label_ace_z_ch4, 5, 6)


        # label for results(temp, rpm and acceralation)
        self.label_temp_ch0_l = QLabel(self)
        self.label_temp_ch1_l = QLabel(self)
        self.label_temp_ch2_l = QLabel(self)

        self.label_rpm_ch0_l = QLabel(self)
        self.label_rpm_ch1_l = QLabel(self)

        self.label_ace_x_ch0_l = QLabel(self)
        self.label_ace_x_ch1_l = QLabel(self)
        self.label_ace_x_ch2_l = QLabel(self)
        self.label_ace_x_ch3_l = QLabel(self)
        self.label_ace_x_ch4_l = QLabel(self)

        self.label_ace_y_ch0_l = QLabel(self)
        self.label_ace_y_ch1_l = QLabel(self)
        self.label_ace_y_ch2_l = QLabel(self)
        self.label_ace_y_ch3_l = QLabel(self)
        self.label_ace_y_ch4_l = QLabel(self)

        self.label_ace_z_ch0_l = QLabel(self)
        self.label_ace_z_ch1_l = QLabel(self)
        self.label_ace_z_ch2_l = QLabel(self)
        self.label_ace_z_ch3_l = QLabel(self)
        self.label_ace_z_ch4_l = QLabel(self)

        # 垂直方向にボタンを並べる
        layout.addWidget(self.label, 0, 1) # dummy

        layout.addWidget(self.label_temp_ch0_l, 1, 1)
        layout.addWidget(self.label_temp_ch1_l, 2, 1)
        layout.addWidget(self.label_temp_ch2_l, 3, 1)

        layout.addWidget(self.label_rpm_ch0_l, 4, 1)
        layout.addWidget(self.label_rpm_ch1_l, 5, 1)

        layout.addWidget(self.label_ace_x_ch0_l, 1, 3)
        layout.addWidget(self.label_ace_x_ch1_l, 2, 3)
        layout.addWidget(self.label_ace_x_ch2_l, 3, 3)
        layout.addWidget(self.label_ace_x_ch3_l, 4, 3)
        layout.addWidget(self.label_ace_x_ch4_l, 5, 3)

        layout.addWidget(self.label_ace_y_ch0_l, 1, 5)
        layout.addWidget(self.label_ace_y_ch1_l, 2, 5)
        layout.addWidget(self.label_ace_y_ch2_l, 3, 5)
        layout.addWidget(self.label_ace_y_ch3_l, 4, 5)
        layout.addWidget(self.label_ace_y_ch4_l, 5, 5)

        layout.addWidget(self.label_ace_z_ch0_l, 1, 7)
        layout.addWidget(self.label_ace_z_ch1_l, 2, 7)
        layout.addWidget(self.label_ace_z_ch2_l, 3, 7)
        layout.addWidget(self.label_ace_z_ch3_l, 4, 7)
        layout.addWidget(self.label_ace_z_ch4_l, 5, 7)

        self.setLayout(layout)

        button = QPushButton('Stop')
        button.clicked.connect(self.__stop)

    def __start(self):
        """開始
        """
        self.signal = Signal()

        if self.wo01.text() == "":
            QMessageBox.information(None, "メッセージ", "作業何号を入力してください", QMessageBox.Ok)
            return
        else:
            logger.file_name(self.wo01.text())

        print(f'start, thread_id={threading.get_ident()}')
        self.__stop()

        self.__thread = QThread()
        self.__thread1 = QThread()
        self.__worker = Worker()
        self.__timer = Timer()

        self.__worker.moveToThread(self.__thread) # 別スレッドで処理を実行する
        self.__timer.moveToThread(self.__thread1) # 別スレッドで処理を実行する

        # シグナルスロットの接続（self.__countup をスレッド側で実行させるために Qt.DirectConnection を指定）
        #self.__worker.countup.connect(self.__countup, type=Qt.DirectConnection)

        self.__worker.signal_result.connect(self.__label, type=Qt.DirectConnection)
        self.__worker.signal_result.connect(self.__logger, type=Qt.DirectConnection)
        self.__timer.signal_elaps1.connect(self.__label, type=Qt.DirectConnection)

        # スレッドが開始されたら worker の処理を開始する
        self.__thread.started.connect(self.__worker.run)
        self.__thread1.started.connect(self.__timer.run)

        # ラムダ式を使う場合は Qt.DirectConnection を指定
        #self.__thread.started.connect(lambda: self.__worker.run(), type=Qt.DirectConnection)
        # スレッドが終了したら破棄する
        self.__thread.finished.connect(self.__worker.deleteLater)
        self.__thread1.finished.connect(self.__timer.deleteLater)

        self.__thread.finished.connect(self.__thread.deleteLater)
        self.__thread1.finished.connect(self.__thread1.deleteLater)

        # 処理開始
        self.__thread.start()
        self.__thread1.start()

    def __stop(self):
        """停止
        """
        print(f'stop, thread_id={threading.get_ident()}')
        if self.__thread and shiboken6.isValid(self.__thread):
            # スレッドが作成されていて、削除されていない
            if self.__thread.isRunning() or not self.__thread.isFinished():
                print('thread is stopping')
                self.__worker.stop()
                self.__timer.stop()
                self.__thread.quit()
                self.__thread1.quit()
                self.__thread.wait()
                self.__thread1.wait()
                print('thread is stopped')


    def __label(self, data):
        """countup シグナルに対する処理
        """

        print(data)

        #print(data)

        if len(data) == 1:
            self.label_elapse1.setText(data[0])

        else:
            # date from logger.py
            self.deta = data[1]

            self.label_temp_ch0_l.setText(str(self.deta[0]))
            self.label_temp_ch1_l.setText(str(self.deta[1]))
            self.label_temp_ch2_l.setText(str(self.deta[2]))
            self.label_rpm_ch0_l.setText(str(self.deta[4]))
            self.label_rpm_ch1_l.setText(str(self.deta[5]))
            self.label_ace_x_ch0_l.setText(str(self.deta[11]))
            self.label_ace_x_ch1_l.setText(str(self.deta[17]))
            self.label_ace_x_ch2_l.setText(str(self.deta[23]))
            self.label_ace_x_ch3_l.setText(str(self.deta[29]))
            self.label_ace_x_ch4_l.setText(str(self.deta[35]))
            self.label_ace_y_ch0_l.setText(str(self.deta[41]))
            self.label_ace_y_ch1_l.setText(str(self.deta[47]))
            self.label_ace_y_ch2_l.setText(str(self.deta[53]))
            self.label_ace_y_ch3_l.setText(str(self.deta[59]))
            self.label_ace_y_ch4_l.setText(str(self.deta[65]))
            self.label_ace_z_ch0_l.setText(str(self.deta[71]))
            self.label_ace_z_ch1_l.setText(str(self.deta[77]))
            self.label_ace_z_ch2_l.setText(str(self.deta[83]))
            self.label_ace_z_ch3_l.setText(str(self.deta[89]))
            self.label_ace_z_ch4_l.setText(str(self.deta[95]))


    def __logger(self, data):

        self.data1 = []

        # date from logger.py
        if len(data) == 1:
            pass

        else:
            self.data = data[1]
            for i in channel_list:
                self.data1.append(self.data[i])

            #logger
            if not os.path.exists(file_path_csv + self.wo01.text() + ".csv"):
                f = open(file_path_csv + self.wo01.text() + ".csv", 'a')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow(header)
                print(header)
                writer.writerow([data[2]] + self.data1)
                f.close()

            else:
                f = open(file_path_csv + self.wo01.text() + ".csv", 'a')
                writer = csv.writer(f, lineterminator='\n')
                writer.writerow([data[2]] + self.data1)
                f.close()

def closeEvent(self, event):
    """closeEvent のオーバーライド（ウィンドウを閉じたときにスレッドを終了させる）
    """
    self.__stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = 'QLabel{color: black; font: 20pt Arial}' # 文字の大きさなど
    app.setStyleSheet(style)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())