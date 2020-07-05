import serial
import sys
import logging
import time
import threading
import numpy
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

__author__ = "Yves Auad"


def _isPython3():
    return sys.version_info[0] >= 3


def SENDMYMESSAGEFUNC(sendmessagefunc):
    return sendmessagefunc


class espec:

    def __init__(self, sendmessage):
        self.sendmessage = sendmessage
        self.ser = serial.Serial()
        self.ser.baudrate = 9600
        self.ser.port = 'COM4'
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.timeout = 0.2

        try:
            if not self.ser.is_open:
                self.ser.open()
                time.sleep(0.1)
        except:
            self.sendmessage(1)

    def set_val(self, val, which):
        if abs(val)<32767:
            try:
                if val < 0: val = 0xffff + val
                string = which + ' 0,' + hex(val)[2:6] + '\r'
                self.ser.write(string.encode())
                return self.ser.read(6)
            except:
                self.sendmessage(2)
        else:
            self.sendmessage(3)

    def wobbler_loop(self, current, intensity, which):
        self.wobbler_thread = threading.currentThread()
        while getattr(self.wobbler_thread, "do_run", True):
            self.set_val(current + intensity, which)
            time.sleep(1.)
            self.set_val(current - intensity, which)
            time.sleep(1.)

    def wobbler_on(self, current, intensity, which):
        self.wobbler_thread = threading.Thread(target=self.wobbler_loop, args=(current, intensity, which), )
        self.wobbler_thread.start()

    def wobbler_off(self):
        self.wobbler_thread.do_run = False


