#!/usr/bin/env python3

from device import Device
from twofg import TWOFG
from vgc10 import VG
from rg2 import RG

if __name__ == '__main__':
    device = Device()
    gripper_2FG7 = TWOFG(device)
    gripper_RG2 = RG(device)
    gripper_VGC10 = VG(device)
