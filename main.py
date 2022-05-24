#!/usr/bin/env python3

from scripts.device import Device
from scripts.twofg import TWOFG

if __name__ == '__main__':
    device = Device()
    device.getCB()
    device.report_robot()
    gripper_2FG7 = TWOFG(device)
    print("Connection check: ", gripper_2FG7.isconn())
