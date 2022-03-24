#!/usr/bin/env python
# -*- coding:utf-8 -*-

# グラフ描写用
import graph

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
import rpm
import temp
import ace

#import usbgpi08

#config.ini関係
parser = configparser.SafeConfigParser() #iniファイルを読込む
parser.read("config.ini") #指定のiniファイルを読込。pyと同じディレクトリーに置くこと
file_path_all = parser.get("File path", "csv") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
file_path_vib = parser.get("File path", "vib") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#com_port1 = parser.get("COM Port", "Port1") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

# キャリブレーション設定
#cal_rpm_ch0 = parser.get("Calibration", "cal_rpm_ch0") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_rpm_ch1 = parser.get("Calibration", "cal_rpm_ch1") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

#cal_tmp_ch0 = parser.get("Calibration", "cal_tmp_ch0") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_tmp_ch1 = parser.get("Calibration", "cal_tmp_ch1") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_tmp_ch2 = parser.get("Calibration", "cal_tmp_ch2") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_tmp_ch3 = parser.get("Calibration", "cal_tmp_ch3") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

# 振動用 vib_chX.py関連 ファイルが開いていたら警告+ファイル削除+ヘッダー作成
# csvファイルが開いていないかの確認、警告を表示
try:
    f = open(file_path_vib, 'a')
    f.close()
except PermissionError:
    QMessageBox.warning(None, "警告", "csvファイルを閉じて下さい!", QMessageBox.Ok)

# ファイル削除
try:
    os.remove(file_path_vib)
except Exception:
    pass

# ヘッダー作成
f = open(file_path_vib, 'a')
writer = csv.writer(f, lineterminator='\n')
csvlist = []
csvlist.append("時間")
csvlist.append("加速度0ch_y")
csvlist.append("加速度0ch_z")
writer.writerow(csvlist)
f.close()

# importされた自作ライブラリに対して渡す値
# 回転数 I/O Adafruit 2264
rpm0 = bytes([0x01,0x80,0x00]) # ch0用
rpm1 = bytes([0x01,0x90,0x00]) # ch1用
#ch2 = bytes([0x01,0xA0,0x00])
#ch3 = bytes([0x01,0xB0,0x00])
#ch4 = bytes([0x01,0xC0,0x00])
#ch5 = bytes([0x01,0xD0,0x00])
#ch6 = bytes([0x01,0xE0,0x00])

# 温度 PhidgetTemp1048
temp0 = 0
temp1 = 1
temp2 = 2
temp3 = 3

# 振動 Phidget Accelerometer
vib0 = 0
vib1 = 1
vib2 = 2
vib3 = 3
vib4 = 4
vib5 = 5


# 未使用 I/O USBGPIO8コマンド
#gpio0 = "adc read " + str(0) + "\r"
#gpio1 = "adc read " + str(1) + "\r"
#gpio2 = "adc read " + str(2) + "\r"
#gpio3 = "adc read " + str(2) + "\r"
#gpio4 = "adc read " + str(2) + "\r"
#gpio5 = "adc read " + str(2) + "\r"
#gpio6 = "adc read " + str(2) + "\r"

# 記録時間用 プログラムを開いた時間
dt = datetime.datetime.now()
dt1 = dt.strftime('%Y/%m/%d')
dt2 = dt.strftime('%H:%M:%S')

class Main(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        #self.qtthread = None
        self.initUI()

        # csvファイルが開いていないかの確認、警告を表示
        try:
            f = open(file_path_all, 'a')
            f.close()
        except PermissionError:
            QMessageBox.warning(None, "警告", "csvファイルを閉じて下さい!", QMessageBox.Ok)

        # ファイル削除
        try:
            os.remove(file_path_all)
        except Exception:
            pass

        # ヘッダー作成
        f = open(file_path_all, 'a')
        writer = csv.writer(f, lineterminator='\n')
        csvlist = []
        csvlist.append("経過時間")
        csvlist.append("時間")
        csvlist.append("回転数 REAR[rpm]")
        csvlist.append("振動値(上下)(REAR プランマーブロック)")
        csvlist.append("振動値(左右)(REAR プランマーブロック)")
        csvlist.append("温度(REAR プランマーブロック)[℃]")
        csvlist.append("振動値(上下)(REAR 台盤)")
        csvlist.append("振動値(左右)(REAR 台盤)")

        csvlist.append("振動値(上下)(ケーシング)")
        csvlist.append("振動値(左右)(ケーシング)")

        csvlist.append("振動値(上下)(FRONT プランマーブロック)")
        csvlist.append("振動値(左右)(FRONT プランマーブロック)")
        csvlist.append("温度(FRONT プランマーブロック)[℃]")
        csvlist.append("振動値(上下)(FRONT 台盤)")
        csvlist.append("振動値(左右)(FRONT 台盤)")

        csvlist.append("トルクアーム[kg]")

        csvlist.append("回転数 FRONT[rpm]")

        csvlist.append("室温[℃]")

        csvlist.append("温度(箱内)[℃]")

        csvlist.append("騒音[℃]")

        writer.writerow(csvlist)
        f.close()

    # GUIni関する設定
    def initUI(self):
        # stylesheetに関する設定
        #self.style1 = "QLabel{color : white; font: 15pt Arial; white; border-color:white; border-style:solid; border-width:1px;}"

        # 表示に関する設定 ラベル
        # 回転数 フィード側 ch0
        self.label_elp_disp = QLabel("経過時間", self)
        self.label_elp_disp.move(165, 10)  # 位置
        self.label_elp_disp.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 回転数 フィード側 ch0
        self.label00_disp = QLabel("回転数   REAR[rpm] 0ch", self)
        self.label00_disp.move(90, 60)  # 位置
        self.label00_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 回転数 減速機側 ch1
        self.label01_disp = QLabel("回転数 FRONT[rpm] 1ch", self)
        self.label01_disp.move(90, 110)  # 位置
        self.label01_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch0
        self.label02_disp = QLabel("温度(REAR   プランマーブロック)[℃] 0ch", self)
        self.label02_disp.move(90, 160)  # 位置
        self.label02_disp.resize(350, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch1
        self.label03_disp = QLabel("温度(FRONT プランマーブロック)[℃] 1ch", self)
        self.label03_disp.move(90, 210)  # 位置
        self.label03_disp.resize(350, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch2
        self.label04_disp = QLabel("温度(室温)[℃] 2ch", self)
        self.label04_disp.move(90, 260)  # 位置
        self.label04_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch3
        self.label05_disp = QLabel("温度(箱内)[℃] 3ch", self)
        self.label05_disp.move(90, 310)  # 位置
        self.label05_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 振動値 y 最小 最大 ch0
        self.label06_disp = QLabel("振動値 左右 (最小 最大) [] 0ch", self)
        self.label06_disp.move(90, 310)  # 位置
        self.label06_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 振動値 z 最小 最大 ch0
        self.label07_disp = QLabel("振動値 上下 (最小 最大) [] 0ch", self)
        self.label07_disp.move(90, 310)  # 位置
        self.label07_disp.resize(250, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 騒音計
        #self.label06_disp = QLabel("騒音 ch2 [dB]", self)
        #self.label06_disp.move(90, 360)  # サイズ
        #self.label05_disp.resize(250, 30)  # サイズ

        # Status Barに関する内容
        self.status_bar1_disp = QLabel("", self)
        self.status_bar1_disp.move(0, 400)
        self.status_bar1_disp.resize(450, 30)


        # 表示に関する設定 測定結果
        # connect ボタンの表示+ボタンとボタンを押した後のプログラムを結びつける
        btn1 = self.auto_button = QPushButton("測定開始", self) # ボタンを表示
        btn1.clicked.connect(self.main)
        btn1.move(20, 10)
        btn1.resize(100, 30)



        # 経過時間
        self.label_elp = QLabel("", self)
        self.label_elp.move(300, 10)  # 位置
        self.label_elp.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)


        # 回転数 フィード側 ch0
        self.label00 = QLabel("", self)
        self.label00.move(20, 60)  # 位置
        self.label00.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 回転数 減速機側 ch1
        self.label01 = QLabel("", self)
        self.label01.move(20, 110)  # 位置
        self.label01.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch0
        self.label02 = QLabel("", self)
        self.label02.move(20, 160)  # 位置
        self.label02.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch1
        self.label03 = QLabel("", self)
        self.label03.move(20, 210)  # 位置
        self.label03.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch2
        self.label04 = QLabel("", self)
        self.label04.move(20, 260)  # 位置
        self.label04.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 熱電対 ch3
        self.label05 = QLabel("", self)
        self.label05.move(20, 310)  # 位置
        self.label05.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 振動値 y 最小 最大 ch0
        self.label06 = QLabel("", self)
        self.label06.move(20, 310)  # 位置
        self.label06.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 振動値 z 最小 最大 ch0
        self.label07 = QLabel("", self)
        self.label07.move(20, 310)  # 位置
        self.label07.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)

        # 騒音計
        #self.label06 = QLabel("", self)
        #self.label06.move(20, 360)  # 位置
        #self.label06.resize(100, 30)  # サイズ
        #self.wo_label1.setStyleSheet(self.style1)


        # 「ラベル - ボタン」を1行として縦方向に並べる グリッドレイアウト
        layout = QFormLayout()
        layout.addRow(btn1, self.status_bar1_disp)
        layout.addRow(self.label_elp, self.label_elp_disp)
        layout.addRow(self.label00, self.label00_disp)
        layout.addRow(self.label01, self.label01_disp)
        layout.addRow(self.label02, self.label02_disp)
        layout.addRow(self.label03, self.label03_disp)
        layout.addRow(self.label04, self.label04_disp)
        layout.addRow(self.label05, self.label05_disp)
        layout.addRow(self.label06, self.label06_disp)
        layout.addRow(self.label07, self.label07_disp)
        layout.setSpacing(20)
        self.setLayout(layout)

        # GUIを表示
        self.show()

    def elp_def(self, xxx): # 経過時間
        self.label_elp.setText("{}".format(xxx))
    def label00_def(self, xxx): # 回転数 フィード側 ch0
        self.label00.setText("{}".format(xxx))
    def label01_def(self, xxx): # 回転数 減速機側 ch1
        self.label01.setText("{}".format(xxx))
    def label02_def(self, xxx): # 熱電対 ch0
        self.label02.setText("{}".format(xxx))
    def label03_def(self, xxx): # 熱電対 ch1
        self.label03.setText("{}".format(xxx))
    def label04_def(self, xxx): # 熱電対 ch2
        self.label04.setText("{}".format(xxx))
    def label05_def(self, xxx): # 熱電対 ch3
        self.label05.setText("{}".format(xxx))
    def label06_def(self, xxx): # 熱電対 ch3
        self.label06.setText("{}".format(xxx))
    def label07_def(self, xxx): # 熱電対 ch3
        self.label07.setText("{}".format(xxx))
    #def label06_def(self, xxx): # 騒音計
    #    self.label06.setText("{}".format(xxx))

    # メインプログラム
    def main(self):
        class Thread(QThread):

            # 一番下の"測定中"の表示に関する設定
            self.styleA = "QWidget{background-color:green; font:14pt Arial}"
            self.status_bar1_disp.setStyleSheet(self.styleA)
            self.status_bar1_disp.setText("                                        測定中")

            # multithreading用のコード GUIの更新+USBへの読み書きなど複数の処理を同時に行うため
            elp_sig = Signal(str)
            rpm0_sig = Signal(str)
            rpm1_sig = Signal(str)
            temp0_sig = Signal(str)
            temp1_sig = Signal(str)
            temp2_sig = Signal(str)
            temp3_sig = Signal(str)
            vib0_y_sig = Signal(str)
            vib0_z_sig = Signal(str)
            #db2_sig = Signal(str)#未使用 騒音用
            #gpio0_sig = Signal(str) # 未使用 usbgpio08.py用

            def run(self):

                # 経過時間
                start = datetime.datetime.now()
                start.strftime('%H:%M:%S')

                while True:
                    # センサーからの測定結果 + キャリブレーション
                    rpm_ch0_result = str(int(rpm_ch0.rpm0(rpm0))*int(cal_rpm_ch0))
                    rpm_ch1_result = str(int(rpm_ch1.rpm1(rpm1))*int(cal_rpm_ch1))

                    temp_ch0_result = str(float(temp_ch0.ch0(temp0))*int(cal_tmp_ch0))
                    temp_ch1_result = str(float(temp_ch1.ch1(temp1))*int(cal_tmp_ch1))
                    temp_ch2_result = str(float(temp_ch2.ch2(temp2))*int(cal_tmp_ch2))
                    temp_ch3_result = str(float(temp_ch3.ch3(temp3))*int(cal_tmp_ch3))

                    # 振動 ch0
                    vib_ch0_result = vib_ch0.vib_port0(vib0)
                    vib_y_min_ch0_result = str(vib_ch0_result[0])
                    vib_y_max_ch0_result = str(vib_ch0_result[1])
                    vib_z_min_ch0_result = str(vib_ch0_result[2])
                    vib_z_max_ch0_result = str(vib_ch0_result[3])

                    # labelに表示するためにsingalとemitを設定
                    self.rpm_0 = self.rpm0_sig.emit(rpm_ch0_result)
                    self.rpm_1 = self.rpm1_sig.emit(rpm_ch1_result)

                    self.tmp_0 = self.temp0_sig.emit(temp_ch0_result)
                    self.tmp_1 = self.temp1_sig.emit(temp_ch1_result)
                    self.tmp_2 = self.temp2_sig.emit(temp_ch2_result)
                    self.tmp_3 = self.temp3_sig.emit(temp_ch3_result)

                    self.vib_0_y = self.vib0_y_sig .emit(vib_y_min_ch0_result + "  " + vib_y_max_ch0_result)
                    self.vib_0_z = self.vib0_z_sig .emit(vib_z_min_ch0_result + "  " + vib_z_max_ch0_result)

                    #self.db2 = self.db2_sig.emit(db_ch2.db2(db2))
                    #self.gpio0 = self. gpio0_sig.emit(usbgpi08.gpio(gpio0)) # 未使用 usbgpio08.py用

                    # 経過時間
                    self.current = datetime.datetime.now()
                    self.cuurent = self.current.strftime('%H:%M:%S')
                    self.elapsed = str(self.current - start)
                    self.elapsed = self.elapsed[0:4]
                    self.elp = self.elp_sig.emit(str(self.elapsed))

                    # 結果を保存
                    self.dt = datetime.datetime.now()
                    self.dt1 = self.dt.strftime('%Y/%m/%d')
                    self.dt2 = self.dt.strftime('%H:%M')
                    f = open(file_path_all, 'a')
                    writer = csv.writer(f, lineterminator='\n')
                    blank = ""
                    csvlist = []

                    csvlist.append(self.elapsed) #経過時間
                    csvlist.append(self.dt2) #時間

                    csvlist.append(rpm_ch0_result) #回転数 REAR[rpm]
                    csvlist.append("'" + str(vib_ch0_result[2]) + "-"+ str(vib_ch0_result[3])) #振動値(上下)(REAR プランマーブロック)
                    csvlist.append("'" + str(vib_ch0_result[0]) + "-"+ str(vib_ch0_result[1])) #振動値(左右)(REAR プランマーブロック)
                    csvlist.append(temp_ch0_result) #温度(REAR プランマーブロック)[℃]
                    csvlist.append("振動値") #振動値(上下)(REAR 台盤)
                    csvlist.append("振動値") #振動値(左右)(REAR 台盤)

                    csvlist.append("振動値") #振動値(上下)(ケーシング)
                    csvlist.append("振動値") #振動値(左右)(ケーシング)

                    csvlist.append("振動値") #振動値(上下)(FRONT プランマーブロック)
                    csvlist.append("振動値") #振動値(左右)(FRONT プランマーブロック)
                    csvlist.append(temp_ch1_result) #温度(FRONT プランマーブロック)[℃]
                    csvlist.append("振動値") #振動値(上下)(FRONT 台盤)
                    csvlist.append("振動値") #振動値(左右)(FRONT 台盤)

                    csvlist.append(blank) #トルクアーム[kg]

                    csvlist.append(rpm_ch1_result)#回転数 FRONT[rpm]

                    csvlist.append(temp_ch2_result) # 室温[℃]

                    csvlist.append(temp_ch3_result) # 箱内温度[℃]
                    #csvlist.append(db_ch2.db2(db2)) #騒音[db]

                    writer.writerow(csvlist)
                    f.close()

                    # 繰返し時間 60sごとに実施
                    time.sleep(60)



        thread = self.qtthread = Thread()
        thread.elp_sig.connect(self.elp_def)
        thread.rpm0_sig.connect(self.label00_def)
        thread.rpm1_sig.connect(self.label01_def)
        thread.temp0_sig.connect(self.label02_def)
        thread.temp1_sig.connect(self.label03_def)
        thread.temp2_sig.connect(self.label04_def)
        thread.temp3_sig.connect(self.label05_def)
        thread.vib0_y_sig.connect(self.label06_def)
        thread.vib0_z_sig.connect(self.label07_def)
        #thread.db2_sig.connect(self.label06_def)

        thread.start()

if __name__ == '__main__':

    app = QApplication(sys.argv) #不明。実行には必ず必要
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2()) #スタイルを変更

    #stylesheetに関する設定
    style2 = 'QLabel{font: 14pt Arial; color: black; border-color:black;}' \
             'QLineEdit{font: 1pt Arial; color: white; border-color: black; ' \
             'border-style:solid; border-width:1px; border-radius:5px}' \
             'QMessageBox{color: white; background-color:white; center;}' \
             'QInputDialog QPushButton{color: white}' \
             'QInputDialog QLineEdit{font: 20pt Arial;}'
    app.setStyleSheet(style2)

    main_window = Main() #class Ppf()を表示
    main_window.setWindowTitle("Final Check Version 0.0.0.1") #windowのtitle
    main_window.setFixedSize(600, 430) #ソフトのサイズとサイズの固定
    #main_window.setStyleSheet('background-color:#19232d')  #ソフトの背景の色を変更
    #main_window.showMaximized()

    # Center Window
    #desktopRect = QApplication.desktop().availableGeometry(main_window)
    #center = desktopRect.center();
    #main_window.move(center.x() - main_window.width() * 0.5,
    #center.y() - main_window.height() * 0.5)

    #main_window.show() #class Ppf()を表示
    app.exec_() #不明。実行には必ず必要



#config.ini関係
#parser = configparser.SafeConfigParser() #iniファイルを読込む
#parser.read("config.ini") #指定のiniファイルを読込。pyと同じディレクトリーに置くこと
#com_port0 = parser.get("COM Port", "Port0") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#com_port1 = parser.get("COM Port", "Port1") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

#COM関係(リレー)
#relay = serial.Serial(com_port1, 9600) #usb通信開始、ポートはconfig.ini, 9600bps
#hex_open = 0xa0, 0x01, 0x01, 0xa2 #Open
#hex_close = 0xa0, 0x01, 0x00, 0xa1 #Close
#usb_com = relay.is_open #usb通信状態確認の変数指定

# COMポート設定
#com_port0 = serial.Serial(com_port0, 115200, timeout=0.1)
#com_open0 = com_port0.is_open



#def gpio4back(self, aaa):
#self.background = (int("{}".format(aaa)))
#print(self.background)
#self.styleA = "QWidget{background-color:%s}" % ("brown" if self.background and self.background < 103 else "green")
#self.status_bar1.setStyleSheet(self.styleA)

#def gpio0back(self, aaa):
#self.background = (int("{}".format(aaa)))
#print(self.background)
#self.styleB = (" Please start the operation" if self.background and self.background < 103 else " Please wait for reaching the operatable pressure")
#self.status_bar1.setText(self.styleB)