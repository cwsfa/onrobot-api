#!/usr/bin/env python3

import time
from device import Device
import numpy as np

'''
XML-RPC library for controlling OnRobot devcies from Doosan robots

Global_cbip holds the IP address of the compute box, needs to be defined by the end user
'''

# Device ID
TWOFG_ID = 0xC0

# Connection
CONN_ERR = -2   # Error
RET_OK = 0      # Okay
RET_FAIL = -1   # Failed


class TWOFG():
    '''
    This class is for handling the 2FG device
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index=0):
        '''
        Returns with True if 2FG device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        try:
            IsTwoFG = self.cb.cb_is_device_connected(t_index, TWOFG_ID)
        except TimeoutError:
            IsTwoFG = False

        if IsTwoFG is False:
            print("No 2FG device connected on the given instance")
            return False
        else:
            return True

    def isBusy(self, t_index=0):
        '''
        Gets if the grpper is busy or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.twofg_get_busy(t_index)

    def isGripped(self, t_index=0):
        '''
        Gets if the gripper is gripping or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if gripped, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.twofg_get_grip_detected(t_index)

    def getStatus(self, t_index=0):
        '''
        Gets the status of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Status code of the device
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        status = self.cb.twofg_get_status(t_index)
        return status

    def get_ext_width(self, t_index=0):
        '''
        Returns with current external width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: External width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        extWidth = self.cb.twofg_get_external_width(t_index)
        return extWidth

    def get_min_ext_width(self, t_index=0):
        '''
        Returns with current minimum external width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Minimum external width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        extMinWidth = self.cb.twofg_get_min_external_width(t_index)
        return extMinWidth

    def get_max_ext_width(self, t_index=0):
        '''
        Returns with current maximum external width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum external width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        extMaxWidth = self.cb.twofg_get_max_external_width(t_index)
        return extMaxWidth

    def get_force(self, t_index=0):
        '''
        Returns with current force

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Force in N
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        currForce = self.cb.twofg_get_force(t_index)
        return currForce

    def halt(self, t_index=0):
        '''
        Stop the grippers movement

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.twofg_stop(t_index)

    def grip_ext(self, t_index=0, t_width=20.0, n_force=20, p_speed=10, f_wait=True):
        '''
        Makes an external grip with the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_width: The width to move the gripper to in mm's
        @type t_width: float
        @param n_force: The force to move the gripper width in N
        @type n_force: float
        @param p_speed: The speed of the gripper in %
        @type p_speed: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        max = self.get_max_ext_width(t_index)
        min = self.get_min_ext_width(t_index)
        if t_width > max or t_width < min:
            print("Invalid 2FG width parameter, " + str(max)+" - "+str(min) +" is valid only")
            return RET_FAIL

        if n_force > 140 or n_force < 20:
            print("Invalid 2FG force parameter, 20-140 is valid only")
            return RET_FAIL

        if p_speed > 100 or p_speed < 10:
            print("Invalid 2FG speed parameter, 10-100 is valid only")
            return RET_FAIL

        self.cb.twofg_grip_external(t_index, float(t_width), int(n_force), int(p_speed))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                time.sleep(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    print("2FG external grip command timeout")
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    time.sleep(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        print("2FG external grip detection timeout")
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    def move(self, t_index, t_width, f_wait):
        '''
        Moves the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_width: The width to move the gripper to in mm's
        @type t_width: float
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_ext_width(t_index)
        min = self.get_min_ext_width(t_index)
        if t_width > max or t_width < min:
            print("Invalid 2FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only")
            return RET_FAIL

        self.cb.twofg_grip_external(t_index, float(t_width), 100, 80)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                time.sleep(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    print("2FG external grip command timeout")
                    break
            else:
                RET_OK
            return RET_FAIL
        else:
            return RET_OK


if __name__ == '__main__':
    device = Device()
    device.getCB()
    gripper_2FG7 = TWOFG(device)
    print("Connection check: ", gripper_2FG7.isconn())
