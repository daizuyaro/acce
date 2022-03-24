# for phidget acceleration ch4
import itertools

from Phidget22.Phidget import *
from Phidget22.Devices.DigitalInput import *
from Phidget22.Devices.Accelerometer import *
import time
import configparser
import csv
import datetime
import math
import scipy.integrate as it
from decimal import Decimal
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import statistics
import matplotlib.pyplot as plt
import ace_phidget

dis_result = []

filepath_csv = "c://a//ace.csv"

samp_int = 0.01 # nr of sampling 10[ms] = 0.01[s]
srt_time = 0 # star time
end_time = 1.27 # end time 0.01[s] x 128[points] 0 is countable as 1

fc_ace = 0.01 # カットオフ周波数
fc_vel = 0.01 # カットオフ周波数
fc_dis = 0.01 # カットオフ周波数

# config.ini関係
#parser = configparser.SafeConfigParser() #iniファイルを読込む
#parser.read("config.ini") #指定のiniファイルを読込。pyと同じディレクトリーに置くこと
#file_path_vib = parser.get("File path", "vib") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

#cal_vib_ch0x = parser.get("Calibration", "cal_vib_ch0x") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_vib_ch0y = parser.get("Calibration", "cal_vib_ch0y") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込
#cal_vib_ch0z = parser.get("Calibration", "cal_vib_ch0z") #NUMATO LAB USBGPI08 config.iniのファイルの指定の列を読込

def ace(port):

    global dis_result

    direction = ace_phidget.main(port)

    for i in [0,1,2]:

        dir = direction[i]

        ace = [n * 9.80665 for n in dir] # g-force -> acceleration 1g = 9.8m/s
        vel = [n * 1/100 for n in ace] # velocity = a*t [m/ms -> m/s] integral period 0-10ms(1/100s)
        dis = [n * 1/2 * (1/100 ** 2) for n in ace] # displacement = 1/2*a*t**2 [acceleration -> displacement]

        # カットオフ周波数決定
        F = np.fft.fft(dis) # FFT
        F_ads = np.abs(F) # for absolute
        # to make axis for data of frequency
        # 周波数変換 周波数軸 linspace(測定開始時間[s],測定終了時間[s]/サンプリング間隔[s](平均サンプリング間隔に変更している),測定数)
        fq = np.linspace(srt_time, end_time/samp_int, len(dis))

        # グラフ表示（FFT解析結果）
        plt.xlabel('freqency(Hz)', fontsize=14)
        plt.ylabel('signal amplitude', fontsize=14)
        # 振幅をもとの信号に揃える
        F_abs_amp = F_ads / len(dis) * 2 # 交流成分はデータ数で割って2倍する
        F_abs_amp[0] = F_abs_amp[0] / 2 # 直流成分（今回は扱わないけど）は2倍不要
        plt.plot(fq, F_abs_amp)
        #plt.show()

        # 周波数でフィルタリング処理 上のplt.showで表示された結果からカットオフ周波数を決定
        F[(fq < fc_dis)] = 0 # カットオフを超える周波数のデータをゼロにする（ノイズ除去)

        # カットオフ周波数の処理したFFT結果の確認
        # FFTの複素数結果を絶対値に変換
        #F2_abs = np.abs(F)
        # 振幅をもとの信号に揃える
        #F2_abs_amp = F2_abs / len(dis) * 2 # 交流成分はデータ数で割って2倍
        #F2_abs_amp[0] = F2_abs_amp[0] / 2 # 直流成分（今回は扱わないけど）は2倍不要

        # グラフ表示（FFT解析結果）
        #plt.xlabel('freqency(Hz)', fontsize=14)
        #plt.ylabel('amplitude', fontsize=14)
        #plt.plot(fq, F2_abs_amp, c='r')
        #plt.show()

        F_ifft = np.fft.ifft(F) # IFFT 逆フーリエ変換 カットオフを適応した値を逆フーリエ変換する
        F_ifft_real = F_ifft.real # 実数部 変位に戻した値

        dis_min = float(np.abs(min(F_ifft_real))) *1000000 # m -> um
        dis_max = float(np.abs(max(F_ifft_real))) *1000000 # m -> um
        dis_min = round(dis_min, 1)
        dis_max = round(dis_max, 1)
        dis_result.append(dis_min)
        dis_result.append(dis_max)

        if len(dis_result) == 6:
            displacement = dis_result
            dis_result = []
            return displacement

        #  #logger
        #if i == 2:
        #    csv_list = [dsp_min, dsp_max]
        #    file_path_all = "c:\\a\\dsp.csv"
        #    f = open(file_path_all, 'a')
        #    writer = csv.writer(f, lineterminator='\n')
        #    writer.writerow(csv_list)
        #    f.close()

    #ace()


