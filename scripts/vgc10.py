#!/usr/bin/env python3

import time
import xmlrpc.client

'''
XML-RPC library for controlling OnRobot devcies from Doosan robots

Global_cbip holds the IP address of the compute box, needs to be defined by the end user
'''

#Device IDs
VG10_ID = 0x10
VGC10_ID = 0x11

CONN_ERR = -2
RET_OK = 0
RET_FAIL = -1


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


class VG():
    '''
    This class is for handling VGC10 devices
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index=0):
        '''
        Returns with True if a VGC10 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        '''
        isVGC10Curr = self.cb.cb_is_device_connected(t_index, VGC10_ID)
        if isVGC10Curr == False:
            print("No VGC10 device connected")
            return False
        else:
            return True

    def grip(self, t_index=0, vacuumA=1, vacuumB=1, waiting=False):
        '''
        Starts the gripper with the given vacuum levels per channel

        @type vacuumA: int
        @type vacuumB: int
        @type waiting: bool
        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param vacuumA: The desired vacuum level on channel A, between 1-80
        @param vacuumB: The desired vacuum level on channel B, between 1-80
        @param waiting: Wait for vacuum to build or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.vg10_grip(t_index, 0, float(vacuumA))
        self.cb.vg10_grip(t_index, 1, float(vacuumB))

        if waiting:
            tim_cnt = 0
            vacA = self.getvacA(t_index)
            vacB = self.getvacB(t_index)
            while ((vacuumA > vacA) or (vacuumB > vacB)):
                time.sleep(0.1)
                vacA = self.getvacA(t_index)
                vacB = self.getvacB(t_index)
                tim_cnt += 1
                if tim_cnt > 40:
                    #Turn off channel that could not reach the level
                    if vacA < vacuumA:
                        self.release(t_index, True, False, False)
                    if vacB < vacuumB:
                        self.release(t_index, False, True, False)
                    print("Timeout during VG grip command")
                    break
            else:
                return RET_OK
            return RET_FAIL
        else:
            return RET_OK

    def release(self, t_index=0, channelA=True, channelB=True, waiting=False):
        '''
        Turns the choosen channels off

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type channelA: bool
        @type channelB: bool
        @type waiting bool
        @param channelA: True turns the channel off, False leaves the channel running
        @param channelB: True turns the channel off, False leaves the channel running
        @param waiting: Wait for complete vacuum loss or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.vg10_release(t_index, channelA, channelB)

        if waiting:
            if (channelA is True) and (channelB is False):
                #Only wait for A channel
                tim_cnt = 0
                vacA = self.getvacA(t_index)
                while (0.1 < vacA):
                    time.sleep(0.1)
                    vacA = self.getvacA(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        print("Timeout during VG release command")
                        break
                else:
                    return RET_OK
                return RET_FAIL
            elif (channelA is False) and (channelB is True):
                #Only wait for B channel
                tim_cnt = 0
                vacB = self.getvacB(t_index)
                while (0.1 < vacB):
                    time.sleep(0.1)
                    vacB = self.getvacB(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        print("Timeout during VG release command")
                        break
                else:
                    return RET_OK
                return RET_FAIL
            elif (channelA is True) and (channelB is True):
                #Wait for both channels
                tim_cnt = 0
                vacA = self.getvacA(t_index)
                vacB = self.getvacB(t_index)
                while ((0.1 < vacB) or (0.1 < vacA)):
                    time.sleep(0.1)
                    vacA = self.getvacA(t_index)
                    vacB = self.getvacB(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        print("Timeout during VG release command")
                        break
                else:
                    return RET_OK
                return RET_FAIL
            else:
                #None of them were commanded to release but wait was True
                #Why would you do this?
                return RET_OK
        else:
            return RET_OK

    def getvacA(self, t_index=0):
        '''
        Returns with vacuum level on channel A

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)

        @rtype: float
        @return: Vacuum level
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        vacAB = self.cb.vg10_get_all_double_variables(t_index)
        if len(vacAB) > 1:
            vacA = vacAB[0]
            return vacA

    def getvacB(self, t_index=0):
        '''
        Returns with vacuum level on channel B

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)

        @rtype: float
        @return: Vacuum level
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        vacAB = self.cb.vg10_get_all_double_variables(t_index)
        if len(vacAB) > 1:
            vacB = vacAB[1]
            return vacB

    def idle(self, t_index=0, channelA=True, channelB=True):
        '''
        Turns off pump on selected channel

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param channelA: True turns the pump off on ch A, False leaves the pump running
        @param channelB: True turns the pump off on ch B, False leaves the pump running
        @type channelA: bool
        @type channelB: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.vg10_idle(t_index, channelA, channelB)


if __name__ == "__main__":
    print('wtf')