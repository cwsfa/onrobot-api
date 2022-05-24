#!/usr/bin/env python3

import xmlrpc.client

'''
XML-RPC library for controlling OnRobot devcies from Doosan robots

Global_cbip holds the IP address of the compute box, needs to be defined by the end user
'''

#Device IDs
VG10_ID = 0x10
VGC10_ID = 0x11
RG2_ID = 0x20
RG6_ID = 0x21
THREEFG_ID = 0x70
TWOFG_ID = 0xC0
MG_ID = 0xA0
SG_ID = 0x50
SD_ID = 0x80
RG2FT_ID = 0x22
VGP_ID = 0x18
SDR_ID = 0xB0
FGP_ID = 0xF0
LIFT_ID = 0x100

#Hex t_index
HEX_INDEX = -1
#HEX device id's
HEXV3_ID = 0x40
HEXV2_ID = 0x42

#LIFT t_index
LIFT_INDEX = 100

EYES_DOOSAN_ID = 8

CONN_ERR = -2
RET_OK = 0
RET_FAIL = -1


class Device:
    '''
    Generic device object
    '''
    cb = None

    def __init__(self):
        #try to get Computebox IP address
        try:
            Global_cbip = '192.168.1.1'
        except NameError:
            tp_popup("Global_cbip is not defined!", DR_PM_WARNING)

    def getCB(self):
            try:
                self.cb = xmlrpc.client.ServerProxy(
                    "http://" + str(Global_cbip) + ":41414/")
                return self.cb
            except TimeoutError:
                tp_popup("Connection to ComputeBox failed!", DR_PM_WARNING)

    def report_robot(self):
        if self.cb is not None:
            #Send our ID to the robot
            self.cb.cb_report_robot_type(EYES_DOOSAN_ID)


class TWOFG():
    '''
    This class is for handling the 2FG device
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if 2FG device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsTwoFG = self.cb.cb_is_device_connected(t_index, TWOFG_ID)
        if IsTwoFG is False:
            tp_popup("No 2FG device connected on the given instance", DR_PM_WARNING)
            return False
        else:
            return True

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
        return self.cb.twofg_get_busy(t_index)

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
        return self.cb.twofg_get_grip_detected(t_index)


    def getStatus(self, t_index):
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

    def get_ext_width(self, t_index):
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

    def get_int_width(self, t_index):
        '''
        Returns with current internal width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Internal width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        intWidth = self.cb.twofg_get_internal_width(t_index)
        return intWidth

    def get_min_ext_width(self, t_index):
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

    def get_min_int_width(self, t_index):
        '''
        Returns with current minimum internal width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Minimum internal width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        intMinWidth = self.cb.twofg_get_min_internal_width(t_index)
        return intMinWidth

    def get_max_ext_width(self, t_index):
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

    def get_max_int_width(self, t_index):
        '''
        Returns with current maximum internal width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum internal width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        intMaxWidth = self.cb.twofg_get_max_internal_width(t_index)
        return intMaxWidth

    def get_force(self, t_index):
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

    def get_finger_len(self, t_index):
        '''
        Returns with current finger length

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Finger length in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        fingerLength = self.cb.twofg_finger_length(t_index)
        return fingerLength

    def get_finger_height(self, t_index):
        '''
        Returns with current finger height

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Finger height in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        fingerHeight = self.cb.twofg_finger_length(t_index)
        return fingerHeight

    def get_finger_orient(self, t_index):
        '''
        Returns with current finger orientation

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Finger orinetation (1 inwards, 2 outwards)
        @rtype: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        fingerOrientation = self.cb.twofg_finger_orientation_outward(t_index)
        return fingerOrientation

    def get_fingertip_offset(self, t_index):
        '''
        Returns with current fingertip offset

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Fingertip offset in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        fingertipOffset = self.cb.twofg_fingertip_offset(t_index)
        return fingertipOffset

    def halt(self, t_index):
        '''
        Stop the grippers movement

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.twofg_stop(t_index)


    def grip_int(self, t_index, t_width, n_force, p_speed, f_wait):
        '''
        Makes an internal grip with the gripper to the desired position

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
        max = self.get_max_int_width(t_index)
        min = self.get_min_int_width(t_index)
        if t_width > max or t_width < min:
            tp_popup("Invalid 2FG width parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if n_force > 140 or n_force < 20:
            tp_popup("Invalid 2FG force parameter, 20-140 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if p_speed > 100 or p_speed < 10:
            tp_popup("Invalid 2FG speed parameter, 10-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_grip_internal(t_index, float(t_width), int(n_force), int(p_speed))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("2FG internal grip command timeout", DR_PM_WARNING)
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("2FG internal grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK


    def grip_ext(self, t_index, t_width, n_force, p_speed, f_wait):
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
            tp_popup("Invalid 2FG width parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if n_force > 140 or n_force < 20:
            tp_popup("Invalid 2FG force parameter, 20-140 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if p_speed > 100 or p_speed < 10:
            tp_popup("Invalid 2FG speed parameter, 10-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_grip_external(t_index, float(t_width), int(n_force), int(p_speed))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("2FG external grip command timeout", DR_PM_WARNING)
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("2FG external grip detection timeout", DR_PM_WARNING)
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
            tp_popup("Invalid 2FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_grip_external(t_index, float(t_width), 100, 80)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("2FG external grip command timeout", DR_PM_WARNING)
                    break
            else:
                RET_OK
            return RET_FAIL
        else:
            return RET_OK


    def set_finger_len(self, t_index, flen):
        '''
        Sets the finger lenght of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param flen: Finger lenght in mm
        @type   flen: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if flen > 100 or flen < 0:
            tp_popup("Invalid 2FG finger length parameter, 0-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_set_finger_length(t_index, float(flen))


    def set_finger_height(self, t_index, fh):
        '''
        Sets the finger height of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param fh: Finger height in mm
        @type   fh: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if fh > 100 or fh < 0:
            tp_popup("Invalid 2FG finger height parameter, 0-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_set_finger_height(t_index, float(fh))

    def set_ft_offset(self, t_index, foffs):
        '''
        Sets the fingertip offset of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param foffs: Fingertip offset in mm
        @type   foffs: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if foffs > 100 or foffs < 0:
            tp_popup("Invalid 2FG fingertip offset parameter, 0-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_set_fingertip_offset(t_index, float(foffs))

    def set_finger_orient(self, t_index, f_orient):
        '''
        Sets the finger orinetation of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param f_orient: Finger orinetation (1 inward, 2 outward)
        @type   f_orient: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if (type(f_orient) != bool):
            tp_popup("Invalid 2FG inward/outward, boolean is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.twofg_set_finger_orientation(t_index, float(f_orient))


class VG():
    '''
    This class is for handling VG10 and VGC10 devices
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if a VG10 or VGC10 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        '''
        isVG10Curr = self.cb.cb_is_device_connected(t_index, VG10_ID)
        isVGC10Curr = self.cb.cb_is_device_connected(t_index, VGC10_ID)
        if isVG10Curr == False and isVGC10Curr == False:
            tp_popup("No VG10 or VGC10 device connected", DR_PM_WARNING)
            return False
        else:
            return True

    def isVGC10(self, t_index):
        '''
        Returns with True if a VGC10 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.cb_is_device_connected(t_index, VGC10_ID)

    def isVG10(self, t_index):
        '''
        Returns with True if a VG10 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.cb_is_device_connected(t_index, VG10_ID)

    def grip(self, t_index, vacuumA, vacuumB, waiting):
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
                wait(0.1)
                vacA = self.getvacA(t_index)
                vacB = self.getvacB(t_index)
                tim_cnt += 1
                if tim_cnt > 40:
                    #Turn off channel that could not reach the level
                    if vacA < vacuumA:
                        self.release(t_index, True, False, False)
                    if vacB < vacuumB:
                        self.release(t_index, False, True, False)
                    tp_popup("Timeout during VG grip command", DR_PM_WARNING)
                    break
            else:
                return RET_OK
            return RET_FAIL
        else:
            return RET_OK

    def release(self, t_index, channelA, channelB, waiting):
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
                    wait(0.1)
                    vacA = self.getvacA(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        tp_popup("Timeout during VG release command", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                return RET_FAIL
            elif (channelA is False) and (channelB is True):
                #Only wait for B channel
                tim_cnt = 0
                vacB = self.getvacB(t_index)
                while (0.1 < vacB):
                    wait(0.1)
                    vacB = self.getvacB(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        tp_popup("Timeout during VG release command", DR_PM_WARNING)
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
                    wait(0.1)
                    vacA = self.getvacA(t_index)
                    vacB = self.getvacB(t_index)
                    tim_cnt += 1
                    if tim_cnt > 40:
                        tp_popup("Timeout during VG release command", DR_PM_WARNING)
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


    def getvacA(self, t_index):
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

    def getvacB(self, t_index):
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

    def idle(self, t_index, channelA, channelB):
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


class RG():
    '''
    This class is for handling RG2 and RG6 devices
    '''
    cb = None

    def __init__(self, dev):
        super().__init__()
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if a RG2 or RG6 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        isRG2Conn = self.cb.cb_is_device_connected(t_index, RG2_ID)
        isRG6Conn = self.cb.cb_is_device_connected(t_index, RG6_ID)
        if not isRG2Conn and not isRG6Conn:
            tp_popup("No RG2 or RG6 device connected", DR_PM_WARNING)
            return False
        else:
            return True

    def isRG2(self, t_index):
        '''
        Returns with True if a RG2 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.cb_is_device_connected(t_index, RG2_ID)

    def isRG6(self, t_index):
        '''
        Returns with True if a RG6 device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.cb_is_device_connected(t_index, RG6_ID)

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
                wait(0.1)
                fbusy = self.cb.rg_get_busy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("RG move timeout", DR_PM_WARNING)
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
                wait(0.1)
                fbusy = self.cb.rg_get_busy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("RG grip timeout", DR_PM_WARNING)
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("RG grip detection timeout", DR_PM_WARNING)
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


class VGP():
    """
    This class is for handling VGP device
    """
    cb = None
    def __init__(self, dev):
        #To hold values before calling grip
        #Indexed by the tool index (single, pri, sec)
        self.required_channels = [0,0,0]
        self.enabled_channels = [0,0,0]
        #To identify channels
        self.ALL_CH = 0x0F
        self.A_CH = 0x01
        self.B_CH = 0x02
        self.C_CH = 0x04
        self.D_CH = 0x08
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if a VGP device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsVGP = self.cb.cb_is_device_connected(t_index, VGP_ID)
        if IsVGP is False:
            tp_popup("No VGP connected on the given instance", DR_PM_WARNING)
            return False
        else:
            return True

    def check_QC(self, t_index):
        '''
        Returns with True if there is a Quick connector error with the device\n
        Should always be used with a High Power Quick Changer

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if QC error, False otherwise
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.vgp_get_error_qc(t_index)

    def check_PSU(self, t_index):
        '''
        Returns with True if there is a PSU error with the device

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if PSU error, False otherwise
        @rtype: bool
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.vgp_get_error_psu(t_index)

    def isBusy(self, t_index):
        '''
        Gets if the gripper is busy or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.vgp_get_busy(t_index)

    def get_vacuum(self, t_index, chID):
        '''
        Gets the current vacuum level for the given channel\n
        Channel needs to be vgp.A_CH, vgp.B_CH, vgp.C_CH or vgp.D_CH

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Vacuum percentage
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if chID == self.A_CH:
            return self.cb.vgp_get_vacuum_a_percent(t_index)
        elif chID == self.B_CH:
            return self.cb.vgp_get_vacuum_b_percent(t_index)
        elif chID == self.C_CH:
            return self.cb.vgp_get_vacuum_c_percent(t_index)
        elif chID == self.D_CH:
            return self.cb.vgp_get_vacuum_d_percent(t_index)
        else:
            tp_popup("Channel parameter needs to be vgp.A_CH or B_CH or C_CH or D_CH", DR_PM_WARNING)
            return RET_FAIL

    def get_release_status(self, t_index, chID):
        '''
        Gets the release status for the given channel\n
        Channel needs to be vgp.A_CH, vgp.B_CH, vgp.C_CH or vgp.D_CH

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Release status\n
        0 means not released
        1 means Release OK
        2 means Release Failed
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if chID == self.A_CH:
            return self.cb.vgp_get_release_status_a(t_index)
        elif chID == self.B_CH:
            return self.cb.vgp_get_release_status_b(t_index)
        elif chID == self.C_CH:
            return self.cb.vgp_get_release_status_c(t_index)
        elif chID == self.D_CH:
            return self.cb.vgp_get_release_status_d(t_index)
        else:
            tp_popup("Channel parameter needs to be vgp.A_CH or B_CH or C_CH or D_CH", DR_PM_WARNING)
            return RET_FAIL

    def get_grip_status(self, t_index, chID):
        '''
        Gets the grip status for the given channel\n
        Channel needs to be vgp.A_CH, vgp.B_CH, vgp.C_CH or vgp.D_CH

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Release status\n
        0 means not gripped
        1 means grip detected
        2 means grip timeout
        3 means grip lost
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if chID == self.A_CH:
            return self.cb.vgp_get_grip_status_a(t_index)
        elif chID == self.B_CH:
            return self.cb.vgp_get_grip_status_b(t_index)
        elif chID == self.C_CH:
            return self.cb.vgp_get_grip_status_c(t_index)
        elif chID == self.D_CH:
            return self.cb.vgp_get_grip_status_d(t_index)
        else:
            tp_popup("Channel parameter needs to be vgp.A_CH or B_CH or C_CH or D_CH", DR_PM_WARNING)
            return RET_FAIL

    #Set required channels to be used for grip
    #Can be called with arbitrary channels
    #Example1: vgp.set_timeout(0, vgp.A_CH, vgp.B_CH) set A and B to time out
    #Example2: vgp.set_timeout(0, vgp.B_CH) set only B to time out
    #Example3: vgp.set_timeout(0, vgp.CH_ALL) set all channels to time out
    def set_timeout(self, t_index, *reqch):
        '''
        Sets the channels to be monitored for timeout during the grip\n
        Channel can be vgp.A_CH, vgp.B_CH, vgp.C_CH, vgp.D_CH, vgp.ALL_CH or combinations of those

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if len(reqch) == 0:
            tp_popup("No channel parameter given to set timeout", DR_PM_WARNING)
            return RET_FAIL

        if len(reqch) > 4:
            tp_popup("Too many channels arguments given to set timeout, max channels is 4", DR_PM_WARNING)
            return RET_FAIL

        if len(reqch) == 1:
            self.required_channels[t_index] = reqch[0]
        else:
            for ch in reqch:
                self.required_channels[t_index] |= ch

        return RET_OK

    #Set enabled channels to be used for grip
    #Can be called with arbitrary channels
    #Example1: vgp.set_grip(0, vgp.A_CH, vgp.B_CH) set A and B to grip
    #Example2: vgp.set_grip(0, vgp.B_CH) set only B to grip
    #Example3: vgp.set_grip(0, vgp.CH_ALL) set all channels
    def set_grip(self, t_index, *enach):
        '''
        Sets the grip channels to be used for grip \n
        Channel can be vgp.A_CH, vgp.B_CH, vgp.C_CH, vgp.D_CH, vgp.ALL_CH or combinations of those

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''

        if len(enach) == 0:
            tp_popup("No channel parameter given to set to grip", DR_PM_WARNING)
            return RET_FAIL

        if len(enach) > 4:
            tp_popup("Too many channels arguments given to set to grip, max channels is 4", DR_PM_WARNING)
            return RET_FAIL

        if len(enach) == 1:
            self.enabled_channels[t_index] = enach[0]
        else:
            for ch in enach:
                self.enabled_channels[t_index] |= ch

        return RET_OK

    #Grip with the previously defined params
    def grip(self, t_index, vac, f_wait):
        '''
        Starts a grip with the previously defined params\n
        set_grip and set_timeout needs to be called before this

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param vac: Vacuum level in kPa (5-60)
        @type vac: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        if vac < 5 or vac > 60:
            tp_popup("Invalid parameter for vacuum level", DR_PM_WARNING)
            return RET_FAIL

        if self.enabled_channels[t_index] == 0:
            tp_popup("Please set up channels with the set_grip command before calling grip", DR_PM_WARNING)

        self.cb.vgp_grip(t_index, int(self.enabled_channels[t_index]), int(self.required_channels[t_index]), int(vac))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("VGP grip command timed out", DR_PM_WARNING)
                    break
            else:
                return RET_OK

            #Grip timeout
            return RET_FAIL

    #Channels list can be arbitrary so it needs to be the last param
    #Can be called with arbitrary channels
    #Example1: vgp.release(0, True, vgp.A_CH, vgp.B_CH) set A and B to grip
    #Example2: vgp.release(0, True,  vgp.B_CH) set only B to grip
    #Example3: vgp.release(0, True,  vgp.CH_ALL) set all channels
    def release(self, t_index, f_wait, *channels):
        '''
        Releases the vacuum on the given channels \n
        Channel can be vgp.A_CH, vgp.B_CH, vgp.C_CH, vgp.D_CH, vgp.ALL_CH or combinations of those

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @type f_wait: bool
        @param f_wait: wait for the release to end or not?
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        rel_channels = 0

        if len(channels) == 0:
            tp_popup("No channels parameter given to release command", DR_PM_WARNING)
            return RET_FAIL

        if len(channels) > 4:
            tp_popup("Too many channels arguments given to release command, max channels is 4", DR_PM_WARNING)
            return RET_FAIL

        if len(channels) == 1:
            rel_channels = channels[0]
        else:
            for ch in channels:
                rel_channels |= ch

        self.cb.vgp_release(t_index, int(rel_channels))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("VGP release command timed out", DR_PM_WARNING)
                    break
            else:
                return RET_OK

            #Release timeout
            return RET_FAIL


class CBIO():
    '''
    This class if for driving Compuetbox IO through a dedicated Weblogic program
    '''
    cb = None
    def __init__(self, dev):
        self.cb = dev.getCB()


    def get_io(self, io_id):
        '''
        Gets the state of the given input id

        @type io_id: int
        @param io_id: Id of the input we want to check (1-8)
        @rtype: bool
        @return: True if INPUT is HIGH, False INPUT is LOW
        '''

        #Sanity check
        if io_id > 8 or io_id < 1:
            tp_popup("Invalid io_id given, 1-8 valid only", DR_PM_WARNING)
            return False

        iostate = self.cb.cb_get_digital_inputs()
        if iostate == -1:
            tp_popup("Failed to get digital input state from computebox", DR_PM_WARNING)
            return False

        if ((iostate & (1 <<(io_id-1))) != 0):
            return True
        else:
            return False

    def get_weblogic_var(self, var_id):
        '''
        Gets the value of the given WebLogic variable id

        @type var_id: int
        @param var_id: Id of the WebLogic variable (0-15)
        @rtype: int
        @return: Value of the variable
        '''
        #Sanity check
        if var_id > 15 or var_id < 1:
            tp_popup("Invalid var_id given, 1-15 valid only", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.cb_get_weblogic_variable(int(var_id))


    def set_weblogic_var(self, var_id, value):
        '''
        Sets the value of the given WebLogic variable id

        @type var_id: int
        @param var_id: Id of the WebLogic variable (0-15)
        @type value: int
        @param value: The value we want to write into the variable
        '''
        #Sanity check
        if var_id > 15 or var_id < 1:
            tp_popup("Invalid var_id given, 1-15 valid only", DR_PM_WARNING)
            return RET_FAIL

        if value > 32767 or value < -32768:
            tp_popup("Invalid value given, -32768-32767 valid only", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.cb_set_weblogic_variable(int(var_id), int(value))

    def start_weblogic_prog(self, prog_id):
        '''
        Starts the given weblogic program

        @type prog_id: int
        @param prog_id: Id of the WebLogic program (0-9999)
        '''
        #if prog_id > 9999 or prog_id < 0:
        #   tp_popup("Invalid prog_id given, 0-9999 valid only", DR_PM_WARNING)
        #    return RET_FAIL

        return self.cb.cb_weblogic_run(prog_id)


    def stop_weblogic_prog(self):
        '''
        Stop the currently running WebLogic program
        '''
        return self.cb.cb_weblogic_stop()

    def set_io(self, io_id, iostate):
        '''
        Sets the state of a Computebox output
        (A dedicated Weblogic program is required to operate)

        @type io_id: int
        @param io_id: Id of the input we want to set (1-8)
        @type iostate: bool
        @param iostate: True - set OUTPUT HIGH, False set OUTPUT LOW
        '''
        #Sanity check
        if io_id > 8 or io_id < 1:
            tp_popup("Invalid io_id given, 1-8 valid only", DR_PM_WARNING)
            return RET_FAIL

        if (type(iostate) != bool):
            tp_popup("Invalid iostate given, boolean is valid only", DR_PM_WARNING)
            return RET_FAIL

        #Set IO through WebLogic
        self.cb.cb_set_weblogic_variable(int(io_id-1), int(iostate))


    def monitor_io(self, io_id):
        '''
        Checks if the given io had a falling edge (pallett removed)
        (A dedicated Weblogic program is required to operate)

        @type io_id: int
        @param io_id: Id of the input we want to set (1-8)
        @rtype: int
        @return: -1 - Error, 1 Input had a falling edge, 0 Input is still 0
        '''
        #Sanity check
        if io_id > 8 or io_id < 1:
            tp_popup("Invalid io_id given, 1-8 valid only", DR_PM_WARNING)
            return RET_FAIL

        ioval = self.cb.cb_get_weblogic_variable(int(io_id+7))

        if ioval > 0:
            return 1
        elif ioval == 0:
            return 0
        else:
            return -1

    def sendpose(self):
        '''
        Sends our current pose (cartesian and joint) to the CB
        '''

        #Get current position from the robot
        curr_pos_tuple = get_current_posx()
        #Convert pos tuple to a dictionary for sending on XML-rpc
        cart_dict = { "x" : curr_pos_tuple[0][0],
            "y" : curr_pos_tuple[0][1],
            "z" : curr_pos_tuple[0][2],
            "r1" : curr_pos_tuple[0][3],
            "r2" : curr_pos_tuple[0][4],
            "r3" : curr_pos_tuple[0][5]
        }
        #Get current joint angles
        curr_posj = get_current_posj()
        #Convert to list so it can be sent over xml-rpc
        joint_list = [0,0,0,0,0,0]
        joint_list[0] = curr_posj[0]
        joint_list[1] = curr_posj[1]
        joint_list[2] = curr_posj[2]
        joint_list[3] = curr_posj[3]
        joint_list[4] = curr_posj[4]
        joint_list[5] = curr_posj[5]

        self.cb.cb_send_pose(cart_dict, joint_list)


class Weblytics():
    '''
    WEBLYTICS - REMOTE PRODUCTION MONITORING AND DEVICE DIAGNOSTIC SOFTWARE
    This class is for weblytics functionality
    '''
    cb = None

    def __init__(self, dev):
        self.WL_VAR_START_INDEX = 32768
        self.WL_VAR_END_INDEX = 65535
        self.WL_SECTION_INDEX = self.WL_VAR_START_INDEX
        self.WL_EVENT_START_INDEX = 32778
        self.WL_CYCLECNT_INDEX = 32868
        self.WL_FAILED_CYCLECNT = 32869
        self.WL_PROGRAMID = 32870
        self.cb = dev.getCB()
        #Init wl user variables to zero
        self._clear()

    def _clear(self):
        '''
        Zero the WL user variables
        '''
        self.cb.cb_set_weblytics_variables(int(self.WL_VAR_START_INDEX), int(self.WL_VAR_END_INDEX), 0)

    # def checkpoint(self, chk_val):
    #     '''
    #     Send a checkpoint to weblytics
    #     @param chk_val: The value of the checkpoint to signal for the weblytics (1-32767)
    #     @type chk_val: int
    #     '''

    #     #Sanity check
    #     if chk_val < 1 or chk_val > 32767:
    #         tp_popup("Invalid parameter for checkpoint value, 1-32767 is valid only", DR_PM_WARNING)
    #         return RET_FAIL

    #     self.cb.cb_set_weblytics_variable(int(self.WL_CHKP_INDEX), int(chk_val))

    def section_start(self, section_id):
        '''
        Send a checkpoint to weblytics
        @param section_id: The ID of the section that we are entering for the weblytics (1-32767)
        @type section_id: int
        '''

        #Sanity check
        if section_id < 1 or section_id > 32767:
            tp_popup("Invalid parameter for section value, 1-32767 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.cb_set_weblytics_variable(int(self.WL_SECTION_INDEX), int(section_id))

    def section_stop(self, section_id):
        '''
        Send a checkpoint to weblytics
        @param section_id: The ID of the section that we are entering for the weblytics (1-32767)
        @type section_id: int
        '''

        #Sanity check
        if section_id < 1 or section_id > 32767:
            tp_popup("Invalid parameter for section value, 1-32767 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.cb_set_weblytics_variable(int(self.WL_SECTION_INDEX), int((-1)*section_id))

    def event(self, event_index):
        '''
        Send an event to weblytics
        Events are available from 1 to 10
        @param event_index: The event to send to weblytics
        @type event_index: int
        @return: Event counter after incrementing
        @rtype: int
        '''

        #Sanity check
        if event_index < 1 or event_index > 10:
            tp_popup("Invalid parameter for event index, 1-10 is valid only", DR_PM_WARNING)
            return RET_FAIL

        wl_event_index = self.WL_EVENT_START_INDEX + event_index -1
        retval = self.cb.cb_increment_weblytics_variable(int(wl_event_index), 1)
        return retval

    def get_event(self, event_index):
        '''
        Get current event value for given index
        Events are available from 1 to 10
        @param event_index: The event to send to weblytics
        @type event_index: int
        @return: Event counter after incrementing
        @rtype: int
        '''

        #Sanity check
        if event_index < 1 or event_index > 10:
            tp_popup("Invalid parameter for event index, 1-10 is valid only", DR_PM_WARNING)
            return RET_FAIL

        wl_event_index = self.WL_EVENT_START_INDEX + event_index -1
        retval = self.cb.cb_increment_weblytics_variable(int(wl_event_index), 0)
        return retval

    def cyclecounter(self):
        '''
        Signal the weblytics that a cycle was done
        @return: The incremented cycle counter value
        @rtype: int
        '''

        retval =self.cb.cb_increment_weblytics_variable(self.WL_CYCLECNT_INDEX, 1)
        return retval

    def get_cyclecounter(self):
        '''
        Get back the current cycle counter value
        @return: The current cycle counter value
        @rtype: int
        '''

        retval = self.cb.cb_increment_weblytics_variable(self.WL_CYCLECNT_INDEX, 0)
        return retval

    def nonprodcycle(self):
        '''
        Signal the weblytics that a non productive cycle happened
        @return: The incremented non productive cycle counter value
        @rtype: int
        '''

        retval = self.cb.cb_increment_weblytics_variable(self.WL_FAILED_CYCLECNT, 1)
        return retval

    def get_nonprodcycle(self):
        '''
        Get back the current non productive cyle counter
        @return: The current non productive cycle counter
        @rtype: int
        '''

        retval = self.cb.cb_increment_weblytics_variable(self.WL_FAILED_CYCLECNT, 0)
        return retval

    def setprogramid(self, prog_id):
        '''
        Send our program ID to the weblytics
        '''
        #Sanity check
        if prog_id < 1 or prog_id > 32767:
            tp_popup("Invalid parameter for checkpoint value, 1-32767 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.cb_set_weblytics_variable(int(self.WL_PROGRAMID), int(prog_id))


'''
Device instances to be used by the user
'''

#Generic device object
or_dev = Device()
or_dev.report_robot()

# or_vgx = VG(or_dev)
# or_rgx = RG(or_dev)
or_2fg = TWOFG(or_dev)
# or_vgp = VGP(or_dev)
# or_cb = CBIO(or_dev)
# or_wl = Weblytics(or_dev)
# or_tfg = THREEFG(or_dev)
# or_eyes = EYES(or_dev)
# or_sg = SG(or_dev)
# or_mg = MG(or_dev)
# or_sdr = SDR(or_dev)
# or_hex = HEX(or_dev)
# or_rg2ft = RG2FT(or_dev)
# or_sd = SD(or_dev)
# or_fgp = FGP(or_dev)
# or_lift = LIFT(or_dev)
