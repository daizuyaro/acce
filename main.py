#!/usr/bin/env python
# -*- coding:utf-8 -*-



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
import rpm_mcp3008
import ace_ch0
import ace_ch1
import ace_ch2
import ace_ch3
import ace_ch4

file_path_all = "c://temp//a.csv"


class MyWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.wo01 = QLineEdit("", self)
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
        self.btn01.resize(400*0.8, 80)
        self.btn01.setStyleSheet("color: black; font: 20pt Arial; border-color: black; "
                                 "border-style:solid; border-width: 1.5px; border-radius:10px") # 文字の大きさなど
        self.btn01.clicked.connect(self.loop)

        self.setGeometry(200, 200, 300, 200)


        layout = QGridLayout()

        # label for channels(temp, rpm and acceralation)
        self.label = QLabel("") # dummy

        self.label_temp_ch0 = QLabel("温度(ch0)")
        self.label_temp_ch1 = QLabel("温度(ch1)")
        self.label_temp_ch2 = QLabel("温度(ch2)")

        self.label_rpm_ch0 = QLabel("回転数(ch0)")
        self.label_rpm_ch1 = QLabel("回転数(ch1)")


        self.label_ace_x_ch0 = QLabel("加速度x(ch0)")
        self.label_ace_x_ch1 = QLabel("加速度x(ch1)")
        self.label_ace_x_ch2 = QLabel("加速度x(ch2)")
        self.label_ace_x_ch3 = QLabel("加速度x(ch3)")
        self.label_ace_x_ch4 = QLabel("加速度x(ch4)")

        self.label_ace_y_ch0 = QLabel("加速度y(ch0)")
        self.label_ace_y_ch1 = QLabel("加速度y(ch1)")
        self.label_ace_y_ch2 = QLabel("加速度y(ch2)")
        self.label_ace_y_ch3 = QLabel("加速度y(ch3)")
        self.label_ace_y_ch4 = QLabel("加速度y(ch4)")

        self.label_ace_z_ch0 = QLabel("加速度z(ch0)")
        self.label_ace_z_ch1 = QLabel("加速度z(ch1)")
        self.label_ace_z_ch2 = QLabel("加速度z(ch2)")
        self.label_ace_z_ch3 = QLabel("加速度z(ch3)")
        self.label_ace_z_ch4 = QLabel("加速度z(ch4)")

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

    def label_connect_0(self, xxx):
        self.label_temp_ch0_l.setText("{}".format(xxx))
    def label_connect_1(self, xxx):
        self.label_temp_ch1_l.setText("{}".format(xxx))
    def label_connect_2(self, xxx):
        self.label_temp_ch2_l.setText("{}".format(xxx))

    def label_connect_3(self, xxx):
        self.label_rpm_ch0_l.setText("{}".format(xxx))
    def label_connect_4(self, xxx):
        self.label_rpm_ch1_l.setText("{}".format(xxx))

    def label_connect_5(self, xxx):
        self.label_ace_x_ch0_l.setText("{}".format(xxx))
    def label_connect_6(self, xxx):
        self.label_ace_x_ch1_l.setText("{}".format(xxx))
    def label_connect_7(self, xxx):
        self.label_ace_x_ch2_l.setText("{}".format(xxx))
    def label_connect_8(self, xxx):
        self.label_ace_x_ch3_l.setText("{}".format(xxx))
    def label_connect_9(self, xxx):
        self.label_ace_x_ch4_l.setText("{}".format(xxx))

    def label_connect_10(self, xxx):
        self.label_ace_y_ch0_l.setText("{}".format(xxx))
    def label_connect_11(self, xxx):
        self.label_ace_y_ch1_l.setText("{}".format(xxx))
    def label_connect_12(self, xxx):
        self.label_ace_y_ch2_l.setText("{}".format(xxx))
    def label_connect_13(self, xxx):
        self.label_ace_y_ch3_l.setText("{}".format(xxx))
    def label_connect_14(self, xxx):
        self.label_ace_y_ch4_l.setText("{}".format(xxx))

    def label_connect_15(self, xxx):
        self.label_ace_z_ch0_l.setText("{}".format(xxx))
    def label_connect_16(self, xxx):
        self.label_ace_z_ch1_l.setText("{}".format(xxx))
    def label_connect_17(self, xxx):
        self.label_ace_z_ch2_l.setText("{}".format(xxx))
    def label_connect_18(self, xxx):
        self.label_ace_z_ch3_l.setText("{}".format(xxx))
    def label_connect_19(self, xxx):
        self.label_ace_z_ch4_l.setText("{}".format(xxx))


    def loop(self):
        class Thread(QThread):

            signal_0 = Signal(str)
            signal_1 = Signal(str)
            signal_2 = Signal(str)
            signal_3 = Signal(str)
            signal_4 = Signal(str)
            signal_5 = Signal(str)
            signal_6 = Signal(str)
            signal_7 = Signal(str)
            signal_8 = Signal(str)
            signal_9 = Signal(str)
            signal_10 = Signal(str)
            signal_11 = Signal(str)
            signal_12 = Signal(str)
            signal_13 = Signal(str)
            signal_14 = Signal(str)
            signal_15 = Signal(str)
            signal_16 = Signal(str)
            signal_17 = Signal(str)
            signal_18 = Signal(str)
            signal_19 = Signal(str)

            def run(self):

                # time for elapse
                start = datetime.datetime.now()
                start.strftime('%H:%M:%S')

                while True:
                    # temperature
                    ch = [0,1,2]
                    list_temp = []
                    for i in ch:
                        value = temp_phidget.temp_phidget(i)
                        list_temp.append(value)
                        if len(list_temp) == 3:
                            self.signal_0.emit(list_temp[0])
                            self.signal_1.emit(list_temp[1])
                            self.signal_2.emit(list_temp[2])
                        else:
                            pass

                    # rpm
                    ch = [bytes([0x01,0x80,0x00]), bytes([0x01,0x90,0x00])] ##訂正しろ
                    list_rpm = []
                    for i in ch:
                        value = rpm_mcp3008.rpm_mcp3008(i)
                        list_rpm.append(value)
                        if len(list_rpm) == 2:
                            self.signal_3.emit(list_rpm[0])
                            self.signal_4.emit(list_rpm[1])
                        else:
                            pass

                    # acceralation
                    port = [0, 1, 2, 3, 4]

                    list_ace = []

                    for port in port:
                        if port == 0:
                            value = ace_ch0.ace(port)
                            self.signal_5.emit(str(value[0]))
                            self.signal_10.emit(str(value[1]))
                            self.signal_15.emit(str(value[2]))

                        elif port == 1:
                            value = ace_ch1.ace(port)
                            self.signal_6.emit(str(value[0]))
                            self.signal_11.emit(str(value[1]))
                            self.signal_16.emit(str(value[2]))

                        elif port == 2:
                            value = ace_ch2.ace(port)
                            self.signal_7.emit(str(value[0]))
                            self.signal_12.emit(str(value[1]))
                            self.signal_17.emit(str(value[2]))

                        elif port == 3:
                            value = ace_ch3.ace(port)
                            self.signal_8.emit(str(value[0]))
                            self.signal_13.emit(str(value[1]))
                            self.signal_18.emit(str(value[2]))

                        elif port == 4:
                            value = ace_ch4.ace(port)
                            self.signal_9.emit(str(value[0]))
                            self.signal_14.emit(str(value[1]))
                            self.signal_19.emit(str(value[2]))

                # time elapsed
                    self.current = datetime.datetime.now()
                    self.cuurent = self.current.strftime('%H:%M:%S')
                    self.elapsed = str(self.current - start)
                    self.elapsed = self.elapsed[0:4]
                    #self.elp = self.elp_sig.emit(str(self.elapsed))

                    #logger
                    csvlist = []
                    list = list_temp + list_rpm + list_ace

                    self.dt = datetime.datetime.now()
                    self.dt1 = self.dt.strftime('%Y/%m/%d')
                    self.dt2 = self.dt.strftime('%H:%M')
                    f = open(file_path_all, 'a')
                    writer = csv.writer(f, lineterminator='\n')

                    csvlist.append(self.elapsed) # time elapsed
                    csvlist.append(self.dt2) # time
                    writer.writerow(list)

                    f.close()

                    # cycle at 60 sec
                    time.sleep(1)


    # thread処理＋connect
        thread = self.thread = Thread()
        thread.signal_0.connect(self.label_connect_0)
        thread.signal_1.connect(self.label_connect_1)
        thread.signal_2.connect(self.label_connect_2)
        thread.signal_3.connect(self.label_connect_3)
        thread.signal_4.connect(self.label_connect_4)
        thread.signal_5.connect(self.label_connect_5)
        thread.signal_6.connect(self.label_connect_6)
        thread.signal_7.connect(self.label_connect_7)
        thread.signal_8.connect(self.label_connect_8)
        thread.signal_9.connect(self.label_connect_9)
        thread.signal_10.connect(self.label_connect_10)
        thread.signal_11.connect(self.label_connect_11)
        thread.signal_12.connect(self.label_connect_12)
        thread.signal_13.connect(self.label_connect_13)
        thread.signal_14.connect(self.label_connect_14)
        thread.signal_15.connect(self.label_connect_15)
        thread.signal_16.connect(self.label_connect_16)
        thread.signal_17.connect(self.label_connect_17)
        thread.signal_18.connect(self.label_connect_18)
        thread.signal_19.connect(self.label_connect_19)
        thread.start()


if __name__ == "__main__":

    # Main process
    app = QApplication(sys.argv)

    style = 'QLabel{color: black; font: 20pt Arial}' # 文字の大きさなど
    app.setStyleSheet(style)

    mywindow = MyWindow()
    mywindow.setWindowTitle("熱変形量監視ソフト Version 0.0.0") # windowのtitle
    #mywindow.showFullScreen()

    scr_w,scr_h= pag.size() #LCD resolution

    mywindow.setFixedSize(scr_w*0.4, scr_h*0.4)  # windows size based on LCD resolution
    mywindow.show()
    app.exec_()