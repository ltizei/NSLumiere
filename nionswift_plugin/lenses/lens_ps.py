import serial
import threading
import os
import json
import logging

from nion.swift.model import HardwareSource

from . import Lens_controller

abs_path = os.path.abspath('C:\ProgramData\Microscope\global_settings.json')
try:
    with open(abs_path) as savfile:
        settings = json.load(savfile)
except FileNotFoundError:
    abs_path = os.path.join(os.path.dirname(__file__), '../aux_files/config/global_settings.json')
    with open(abs_path) as savfile:
        settings = json.load(savfile)

MAX_OBJ = settings["lenses"]["MAX_OBJ"]
MAX_C1 = settings["lenses"]["MAX_C1"]
MAX_C2 = settings["lenses"]["MAX_C2"]

__author__ = "Yves Auad"

class Lenses(Lens_controller.LensesController):

    def __init__(self, sport):
        super().__init__()
        self.success = False
        self.ser = serial.Serial()
        self.ser.baudrate = 57600
        self.ser.port = sport
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.timeout = 0.2

        self.lock = threading.Lock()

        try:
            if not self.ser.is_open:
                self.ser.open()
            self.success = True
        except:
            logging.info("***LENSES***: Could not find Lenses PS. Entering in debug mode.")

    def query(self, which):
        if which == 'OBJ':
            string = '>1,2,1\r'
        if which == 'C1':
            string = '>1,2,2\r'
        if which == 'C2':
            string = '>1,2,3\r'
        try:
            self.ser.write(string.encode())
            self.ser.read(7)
            current = self.ser.read_until(expected=b','); current = current[:-1]
            voltage = self.ser.read_until(expected=b','); voltage = voltage[:-1]
            self.ser.readline()
        except:
            logging.info('***LENSES***: Communication Error over Serial Port. Easy check using Serial Port '
                         'Monitor software.')
        return current, voltage

    def set_val(self, val, which):
        if which == 'OBJ_STIG':
            scan = HardwareSource.HardwareSourceManager().get_hardware_source_for_hardware_source_id("orsay_scan_device")
            if scan is not None:
                scan.scan_device.orsayscan.ObjectiveStigmateur(val[0] / 1000., val[1] / 1000.)
            else:
                logging.info('***LENSES***: Could not find objetive stigmator.')
            return
        if which == 'GUN_STIG':
            scan = HardwareSource.HardwareSourceManager().get_hardware_source_for_hardware_source_id(
                "orsay_scan_device")
            if scan is not None:
                scan.scan_device.orsayscan.CondensorStigmateur(val[0] / 1000., val[1] / 1000.)
            else:
                logging.info('***LENSES***: Could not find gun stigmator.')
            return
        if which == 'OBJ' and val<=MAX_OBJ and val>=0:
            string_init = '>1,1,1,'
        elif which == 'C1' and val<=MAX_C1 and val>=0:
            string_init = '>1,1,2,'
        elif which == 'C2' and val<=MAX_C2 and val>=0:
            string_init = '>1,1,3,'
        else:
            logging.info("***LENSES***: Attempt to set values out of range.")
            return None

        string = string_init + str(val) + ',0.5\r'
        self.ser.write(string.encode())
        return self.ser.readline()