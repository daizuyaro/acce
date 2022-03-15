#!/usr/bin/env python
# -*- coding:utf-8 -*-

from pyftdi.spi import SpiController
import time
from multiprocessing import Process, Queue, pool
import multiprocessing as mp
import asyncio
import csv
import datetime

file_path_all = "c://temp//b.csv"


start = time.perf_counter()
cycle = 0
cofficient = 60

# Instantiate a SPI controller
# We need want to use A*BUS6 for /CS, so at least 2 /CS lines should be
# reserved for SPI, the remaining IO are available as GPIOs.
spi = SpiController()

# Configure the first interface (IF/1) of the FTDI device as a SPI master
spi.configure('ftdi://ftdi:232h:1/1')

# Get a port to a SPI slave w/ /CS 0 and SPI mode 0 @ 20MHz
# mode=0 or 3 にする。ch0=mode=0 ch1=mode=0にする
slave = spi.get_port(cs=0, freq=20000000, mode=0) #cs:chip select

# Synchronous exchange with the remote SPI slave
#ch0 = bytes([0x01,0x80,0x00])
#ch1 = bytes([0x01,0x90,0x00])

def rpm_mcp3008(ch):
    global cycle
    global rpm

    end = time.perf_counter() + 1

    while True:
        read_buf = slave.exchange(ch, duplex=True)
        data = ((read_buf[1]&3) << 8) + read_buf[2]
        start = time.perf_counter()

        print(data)

        if start <= end:
            if data < 50:
                cycle += 1
                time.sleep(0.01)

        else:
            rpm = cycle * cofficient
            cycle = 0

            return str(rpm)