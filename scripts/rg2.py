#!/usr/bin/env python3

import time
import numpy as np
import xmlrpc.client

'''
XML-RPC library for controlling OnRobot devcies from Doosan robots

Global_cbip holds the IP address of the compute box, needs to be defined by the end user
'''

#Device IDs
RG2_ID = 0x20

# Connection
CONN_ERR = -2   # Error
RET_OK = 0      # Okay
RET_FAIL = -1   # Failed

class Device:
    '''
    Generic device object
    '''
    cb = None

    def __init__(self, Global_cbip='192.168.1.1'):
        #try to get Computebox IP address
        try:
            self.Global_cbip = Global_cbip
        except NameError:
            print("Global_cbip is not defined!")

    def getCB(self):
            try:
                self.cb = xmlrpc.client.ServerProxy(
                    "http://" + str(self.Global_cbip) + ":41414/")
                return self.cb
            except TimeoutError:
                print("Connection to ComputeBox failed!")


class RG():
    '''
    This class is for handling RG2 devices
    '''
    cb = None

    def __init__(self, dev):
        super().__init__()
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if a RG2 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        isRG2Conn = self.cb.cb_is_device_connected(t_index, RG2_ID)
        if not isRG2Conn:
            print("No RG2 device connected")
            return False
        else:
            return True

    #No grip detection (just move the gripper)
    def move(self, t_index, twidth, tforce, fwait):
        '''
        Moves the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param twidth: The width to move the gripper to in mm's
        @type twidth: float
        @param tforce: The force to move the gripper width in Newtons
        @type fwait: bool
        @param fwait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.rg_grip(t_index, float(twidth), float(tforce))

        if fwait:
            tim_cnt = 0
            fbusy = self.cb.rg_get_busy(t_index)
            while (fbusy):
                time.sleep(0.1)
                fbusy = self.cb.rg_get_busy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    print("RG move timeout")
                    break
            else:
                return RET_OK

            return RET_FAIL
        else:
            return RET_OK

    #If wait then also detect grip at the end
    def grip(self, t_index, twidth, tforce, fwait):
        '''
        Makes a grip with the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param twidth: The width to move the gripper to in mm's
        @type twidth: float
        @param tforce: The force to move the gripper width in Newtons
        @type fwait: bool
        @param fwait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.rg_grip(t_index, float(twidth), float(tforce))

        if fwait:
            tim_cnt = 0
            fbusy = self.cb.rg_get_busy(t_index)
            while (fbusy):
                time.sleep(0.1)
                fbusy = self.cb.rg_get_busy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    print("RG grip timeout")
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
                        print("RG grip detection timeout")
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    def halt(self, t_index):
        '''
        Stop the grippers movement

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_stop(t_index)

    def get_speed(self, t_index):
        '''
        Returns with the grippers speeds

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: Speed in mm/s
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_speed(t_index)

    def get_depth(self, t_index):
        '''
        Gets the absolute depth of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: Depth in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_depth(t_index)

    def get_rel_depth(self, t_index):
        '''
        Gets the relative depth of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: Depth in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_relative_depth(t_index)

    def get_width(self, t_index):
        '''
        Gets the width of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: Width in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_width(t_index)

    def get_ft_offset(self, t_index):
        '''
        Gets the current fingertip offset of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: Fingertip offset in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_fingertip_offset(t_index)

    def isBusy(self, t_index):
        '''
        Gets if the grpper is busy or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_busy(t_index)

    def isGripped(self, t_index):
        '''
        Gets if the gripper is gripping or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if gripped, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_get_grip_detected(t_index)

    def isSafetyON(self, t_index):
        '''
        Gets if the safety circuit is active or no

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if safety triggered, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        s1 = self.cb.rg_get_s1_triggered(t_index)
        s2 = self.cb.rg_get_s2_triggered(t_index)
        if (s1 or s2):
            return True
        elif (not s1 and not s2):
            return False

    def set_ft_offset(self, t_index, ft_offset):
        '''
        Sets the fingertip offset of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param ft_offset: Finger tip offset
        @type   ft_offset: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.rg_set_fingertip_offset(t_index, float(ft_offset))

    def resetpower(self, t_index):
        '''
        Resets the power of the grippers\n
        Needs to be issued after saftey event

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.cb_reset_tool_power()


if __name__ == '__main__':
    device = Device()
    device.getCB()
    gripper_RG2 = RG(device)
    print("Connection check: ", gripper_RG2.isconn())
