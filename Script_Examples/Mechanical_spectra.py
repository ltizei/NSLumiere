from nion.utils import Registry
from nion.swift.model import HardwareSource
import numpy
import time

cam = HardwareSource.HardwareSourceManager().get_hardware_source_for_hardware_source_id("orsay_camera_eels")
scan = HardwareSource.HardwareSourceManager().get_hardware_source_for_hardware_source_id("orsay_scan_device")
stage = HardwareSource.HardwareSourceManager().get_instrument_by_id("stage_controller")
my_inst = HardwareSource.HardwareSourceManager().get_instrument_by_id("VG_Lum_controller")

pts = 8

xarray = numpy.linspace(0, 1, pts)
yarray = numpy.linspace(0, 1, pts)

fov = scan.scan_device.field_of_view
ia = scan.scan_device.Image_area

x_samp = (fov*1e9)/(ia[3]-ia[2])
y_samp = (fov*1e9)/(ia[5]-ia[4])

initial_stage_x = stage.x_pos_f
initial_stage_y = stage.y_pos_f

initial_probe_x = scan.scan_device.probe_pos[0]
initial_probe_y = scan.scan_device.probe_pos[1]

print('Sampling: ')
print(x_samp)
print(y_samp)
print('# Pixels step: :')
print((ia[3]-ia[2])/pts)
print((ia[5]-ia[4])/pts)

sen = 1
for x in xarray:
    stage.x_pos_f+=x_samp/10 * (ia[3]-ia[2])/pts
    sen = sen * -1
    for y in yarray:
        if not my_inst._ivgInstrument__stage_moving:
            stage.y_pos_f+=y_samp/10 * sen * (ia[5]-ia[4])/pts
            print([stage.x_pos_f/100, stage.y_pos_f/100])
            scan.scan_device.probe_pos = (x, y)
        time.sleep(0.05)


stage.x_pos_f = initial_stage_x
stage.y_pos_f = initial_stage_y