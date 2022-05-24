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
            Global_cbip
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


class THREEFG():
    '''
    This class is for handling 3FG device
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if 3FG device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        is3FGConn = self.cb.cb_is_device_connected(t_index, THREEFG_ID)
        if not is3FGConn:
            tp_popup("No 3FG device connected", DR_PM_WARNING)
            return False
        else:
            return True

    def get_min_diam(self, t_index):
        '''
        Returns with current minimum diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Minimum diameter in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_min_diameter(t_index)

    def get_max_diam(self, t_index):
        '''
        Returns with current maximum diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum diameter in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_max_diameter(t_index)

    def get_diam(self, t_index):
        '''
        Returns with current diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return:  Diameter in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_diameter(t_index)

    def get_raw_diam(self, t_index):
        '''
        Returns with current raw diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Raw diameter in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_diameter_raw(t_index)

    def get_force(self, t_index):
        '''
        Returns with current force

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Force in N
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_force(t_index)

    def get_finger_pos(self, t_index):
        '''
        Returns with current finger position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Finger position [1,2,3]
        @rtype: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_finger_position(t_index)

    def get_finger_len(self, t_index):
        '''
        Returns with current finger lenght

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Finger lenght in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_finger_length(t_index)

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
        return self.cb.tfg_get_busy(t_index)

    def isForceGripped(self, t_index):
        '''
        Gets if the gripper is force gripping or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if force gripped, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        return self.cb.tfg_get_force_grip_detected(t_index)

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
        return self.cb.tfg_get_grip_detected(t_index)

    def move(self, t_index, diam, f_wait):
        '''
        Moves the gripper to the desired diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param diam: The diameter to move the gripper to in mm's
        @type diam: float
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_diam(t_index)
        min = self.get_min_diam(t_index)

        if ((diam > max) or (diam < min)):
            tp_popup("Invalid 3FG diameter parameter", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_move(t_index, float(diam))

        if f_wait:
            busy_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("3FG move timeout", DR_PM_WARNING)
                    break
            else:
                return RET_OK
            return RET_FAIL
        else:
            return RET_OK

    def grip_int(self, t_index, diam, force, f_wait):
        '''
        Makes an internal grip with the gripper to the desired diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param diam: The diameter to move the gripper to in mm
        @type diam: float
        @param force: The force to move the gripper width in N
        @type force: float
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_diam(t_index)
        min = self.get_min_diam(t_index)

        if ((diam > max) or (diam < min)):
            tp_popup("Invalid 3FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if ((force < 1) or (force > 100)):
            tp_popup("Invalid 3FG force parameter, 1-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_grip(t_index, float(diam), float(force), True)

        if f_wait:
            busy_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("3FG grip timeout", DR_PM_WARNING)
                    break
            else:
                #Check for grip detect
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("3FG grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    #Check for force grip
                    fgrip_tim = 0
                    fgripped = self.isForceGripped(t_index)
                    while (not fgripped):
                        wait(0.1)
                        fgripped = self.isForceGripped(t_index)
                        fgrip_tim += 1
                        if fgrip_tim > 20:
                            tp_popup("3FG force grip detection timeout", DR_PM_WARNING)
                            break
                    else:
                        return RET_OK
                    return RET_FAIL
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK


    def flex_grip_int(self, t_index, diam, force, f_wait):
        '''
        Makes an internal flexible grip with the gripper to the desired diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param diam: The diameter to move the gripper to in mm
        @type diam: float
        @param force: The force to move the gripper width in N
        @type force: float
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_diam(t_index)
        min = self.get_min_diam(t_index)

        if ((diam > max) or (diam < min)):
            tp_popup("Invalid 3FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if ((force < 1) or (force > 100)):
            tp_popup("Invalid 3FG force parameter, 1-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_flexible_grip(t_index, float(diam), float(force), True)

        if f_wait:
            busy_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("3FG grip timeout", DR_PM_WARNING)
                    break
            else:
                #Check for grip detect
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("3FG grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    #Check for force grip
                    fgrip_tim = 0
                    fgripped = self.isForceGripped(t_index)
                    while (not fgripped):
                        wait(0.1)
                        fgripped = self.isForceGripped(t_index)
                        fgrip_tim += 1
                        if fgrip_tim > 20:
                            tp_popup("3FG force grip detection timeout", DR_PM_WARNING)
                            break
                    else:
                        return RET_OK
                    return RET_FAIL
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK



    def grip_ext(self, t_index, diam, force, f_wait):
        '''
        Makes an external grip with the gripper to the desired diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param diam: The diameter to move the gripper to in mm
        @type diam: float
        @param force: The force to move the gripper width in N
        @type force: float
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_diam(t_index)
        min = self.get_min_diam(t_index)

        if ((diam > max) or (diam < min)):
            tp_popup("Invalid 3FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if ((force < 1) or (force > 100)):
            tp_popup("Invalid 3FG force parameter, 1-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_grip(t_index, float(diam), float(force), False)

        if f_wait:
            busy_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("3FG grip timeout", DR_PM_WARNING)
                    break
            else:
                #Check for grip detect
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("3FG grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    #Check for force grip
                    fgrip_tim = 0
                    fgripped = self.isForceGripped(t_index)
                    while (not fgripped):
                        wait(0.1)
                        fgripped = self.isForceGripped(t_index)
                        fgrip_tim += 1
                        if fgrip_tim > 20:
                            tp_popup("3FG force grip detection timeout", DR_PM_WARNING)
                            break
                    else:
                        return RET_OK
                    return RET_FAIL
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    def flex_grip_ext(self, t_index, diam, force, f_wait):
        '''
        Makes an external flexible grip with the gripper to the desired diameter

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param diam: The diameter to move the gripper to in mm
        @type diam: float
        @param force: The force to move the gripper width in N
        @type force: float
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        max = self.get_max_diam(t_index)
        min = self.get_min_diam(t_index)

        if ((diam > max) or (diam < min)):
            tp_popup("Invalid 3FG diameter parameter, " + str(max)+" - "+str(min) +" is valid only", DR_PM_WARNING)
            return RET_FAIL

        if ((force < 1) or (force > 100)):
            tp_popup("Invalid 3FG force parameter, 1-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_flexible_grip(t_index, float(diam), float(force), False)

        if f_wait:
            busy_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("3FG grip timeout", DR_PM_WARNING)
                    break
            else:
                #Check for grip detect
                grip_tim = 0
                gripped = self.isGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("3FG grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    #Check for force grip
                    fgrip_tim = 0
                    fgripped = self.isForceGripped(t_index)
                    while (not fgripped):
                        wait(0.1)
                        fgripped = self.isForceGripped(t_index)
                        fgrip_tim += 1
                        if fgrip_tim > 20:
                            tp_popup("3FG force grip detection timeout", DR_PM_WARNING)
                            break
                    else:
                        return RET_OK
                    return RET_FAIL
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    def set_finger_pos(self, t_index, fpos):
        '''
        Sets the finger position of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param fpos: Finger position [1,2,3]
        @type fpos: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if fpos not in [1,2,3]:
            tp_popup("Invalid 3FG finger position parameter, 1, 2, 3 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_set_finger_position(t_index, fpos)

    def set_finger_len(self, t_index, flen):
        '''
        Sets the finger lenght of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param flen: Finger length
        @type flen: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if flen < 0 or flen> 100:
            tp_popup("Invalid 3FG finger length parameter, 0-100 is valid", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_set_finger_length(t_index, float(flen))

    def set_finger_offset(self, t_index, foffs):
        '''
        Sets the fingertip offset of the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param foffs: Finger tip offset
        @type foffs: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if foffs < 0 or foffs> 100:
            tp_popup("Invalid 3FG finger offset parameter, 0-100 is valid", DR_PM_WARNING)
            return RET_FAIL

        self.cb.tfg_set_fingertip_offset(t_index, float(foffs))



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


class FGP():
    '''
    This class is for controlling the 2FGP20 palletizing gripper
    '''
    cb = None
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if an FGP device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsFGP = self.cb.cb_is_device_connected(t_index, FGP_ID)
        if IsFGP is False:
            tp_popup("No FGP connected on the given instance", DR_PM_WARNING)
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
        return self.cb.fgp_get_busy(t_index)

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
        return self.cb.fgp_get_fg_grip_detected(t_index)

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
        status = self.cb.fgp_get_status(t_index)
        return status

    def get_width(self, t_index):
        '''
        Returns with current external width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: External width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        width = self.cb.fgp_get_external_width(t_index)
        return round(width, 2)

    def get_min_width(self, t_index):
        '''
        Returns with current minimum width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Minimum internal width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        minWidth = self.cb.twofg_get_min_external_width(t_index)
        return minWidth

    def get_max_width(self, t_index):
        '''
        Returns with current maximum width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum external width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        extMaxWidth = self.cb.twofg_get_max_external_width(t_index)
        return extMaxWidth

    def get_force(self, t_index):
        '''
        Returns with current force

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Force in N
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        currForce = self.cb.fgp_get_force(t_index)
        return currForce

    def get_finger_len(self, t_index, p_finger):
        '''
        Returns with current finger length of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)

        @return: Finger length in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if (p_finger == 1):
            fingerLength = self.cb.fgp_get_fixed_finger_length(t_index)
        elif (p_finger == 2):
            fingerLength = self.cb.fgp_get_moving_finger_length(t_index)
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL

        return round(fingerLength, 2)

    def get_finger_height(self, t_index, p_finger):
        '''
        Returns with current finger height of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)

        @return: Finger height in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if (p_finger == 1):
            fingerHeight = self.cb.fgp_get_fixed_finger_height(t_index)
        elif (p_finger == 2):
            fingerHeight = self.cb.fgp_get_moving_finger_height(t_index)
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL

        return round(fingerHeight, 2)

    def get_pad_offset(self, t_index, p_finger):
        '''
        Returns with current pad offset of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)

        @return: Pad offset in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if (p_finger == 1):
            f_offs = self.cb.fgp_get_fixed_fingertip_offset(t_index)
        elif (p_finger == 2):
            f_offs = self.cb.fgp_get_moving_fingertip_offset(t_index)
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL

        return round(f_offs, 2)

    def halt(self, t_index):
        '''
        Stop the grippers movement

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        self.cb.fgp_fg_stop(t_index)

    def set_finger_len(self, t_index, p_finger, flen):
        '''
        Sets the finger lenght of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)
        @type p_finger: int
        @param flen: Finger lenght in mm
        @type   flen: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if flen > 1000 or flen < -300:
            tp_popup("Invalid FGP finger length parameter, -300-1000 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if (p_finger == 1):
            self.cb.fgp_set_fixed_finger_length(t_index, float(flen))
        elif (p_finger == 2):
            self.cb.fgp_set_moving_finger_length(t_index, float(flen))
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL


    def set_finger_height(self, t_index, p_finger, fheight):
        '''
        Sets the finger height of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)
        @type p_finger: int
        @param fheight: Finger height in mm
        @type   fheight: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if fheight > 1000 or fheight < 0:
            tp_popup("Invalid FGP finger height parameter, 0-1000 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if (p_finger == 1):
            self.cb.fgp_set_fixed_finger_height(t_index, float(fheight))
        elif (p_finger == 2):
            self.cb.fgp_set_moving_finger_height(t_index, float(fheight))
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL

    def set_pad_offset(self, t_index, p_finger, foffs):
        '''
        Sets the pad offset of the selected finger

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param p_finger: Finger selector (1 for fixed finger, 2 for moving finger)
        @type p_finger: int
        @param foffs: Pad offset in mm
        @type   foffs: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if foffs > 100 or foffs < 1:
            tp_popup("Invalid FGP fingertip offset parameter, 1-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if (p_finger == 1):
            self.cb.fgp_set_fixed_fingertip_offset(t_index, float(foffs))
        elif (p_finger == 2):
            self.cb.fgp_set_moving_fingertip_offset(t_index, float(foffs))
        else:
            tp_popup("Invalid argument for FGP finger selector (1 or 2 valid only)", DR_PM_WARNING)
            return RET_FAIL


    def get_vac_level(self, t_index):
        '''
        Gets the vacuum level on the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @return: Vacuum level in kPa
        @rtype: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        v_level = self.cb.fgp_get_vg_vacuum_percent(t_index)
        return v_level

    def set_vac_offset(self, t_index, vac_offs):
        '''
        Sets the vacuum cup offset. Distance from the vacuum cup plane to the body of the gripper.

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param vac_offs: distance of the vacuum cup from the body of the gripper in mm
        @type vac_offs: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if vac_offs > 100 or vac_offs < 0:
            tp_popup("Invalid FGP vacuum offset parameter, -1000-1000 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.fgp_set_vg_vacuum_cups_offset(int(t_index), float(vac_offs))


    def get_vac_offset(self, t_index):
        '''
        Gets the vacuum cup offset on the gripper

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @return: Vacuum cup offset in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        v_offs = self.cb.fgp_get_vacuum_cups_offset(t_index)
        return v_offs

    def isVGGripped(self, t_index):
        '''
        Gets if the vacuum gripper is gripping or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @return: True if VG gripped, False otherwise
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR


        v_stat = self.cb.fgp_get_vg_grip_status(t_index)

        if (v_stat == 1):
            return True
        else:
            return False

    def hasError(self, t_index):
        '''
        Gets if the device has an active error flag or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @return: True if FGP has error, False no errors present
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        mot_err = self.cb.fgp_get_error_motor_not_calibrated(t_index)
        sol_err = self.cb.fgp_get_error_solenoid_not_calibrated(t_index)
        enc_err = self.cb.fgp_get_error_encoders_not_calibrated(t_index)

        if (mot_err == sol_err == enc_err == False):
            return False
        else:
            return True

    def grip(self, t_index, t_width, n_force, p_speed, f_wait):
        '''
        Makes a grip with the gripper to the desired position

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
        #max_w = self.get_max_width(t_index)
        #min_w = self.get_min_width(t_index)
        #if t_width > max_w or t_width < min_w:
        #    tp_popup("Invalid FGP width parameter, " + str(max_w)+" - "+str(min_w) +" is valid only", DR_PM_WARNING)
        #    return RET_FAIL

        if n_force > 400 or n_force < 80:
            tp_popup("Invalid FGP force parameter, 20-140 is valid only", DR_PM_WARNING)
            return RET_FAIL

        if p_speed > 100 or p_speed < 10:
            tp_popup("Invalid FGP speed parameter, 10-100 is valid only", DR_PM_WARNING)
            return RET_FAIL

        self.cb.fgp_grip_external(t_index, float(t_width), int(n_force), int(p_speed))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("FGP grip command timeout", DR_PM_WARNING)
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
                        tp_popup("FGP grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK


    def release(self, t_index, t_width, p_speed, f_wait):
        '''
        Moves the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_width: The width to move the gripper to in mm's
        @type t_width: float
        @param p_speed: The speed of the gripper in %
        @type p_speed: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        # max_w = self.get_max_width(t_index)
        # min_w = self.get_min_width(t_index)
        # if t_width > max_w or t_width < min_w:
        #     tp_popup("Invalid FGP diameter parameter, " + str(max_w)+" - "+str(min_w) +" is valid only", DR_PM_WARNING)
        #     return RET_FAIL

        if p_speed > 100 or p_speed < 10:
            tp_popup("Invalid FGP speed parameter, 10-100 is valid only", DR_PM_WARNING)
            return RET_FAIL


        self.cb.fgp_grip_external(t_index, float(t_width), int(80), int(p_speed))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("FGP release command timeout", DR_PM_WARNING)
                    break
            else:
                RET_OK
            return RET_FAIL
        else:
            return RET_OK

    def vacuum_grip(self, t_index, t_vac, f_wait):
        '''
        Makes a grip with the gripper to the desired position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_vac: The target level of vacuum in kPa
        @type t_vac: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        if t_vac > 60 or t_vac < 5:
            tp_popup("Invalid FGP vacuum level parameter, 5-60 is valid only", DR_PM_WARNING)
            return RET_FAIL

        #True is the required flag that is still there but not used
        self.cb.fgp_vg_grip(t_index, True, int(t_vac))

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("FGP vacuum grip command timeout", DR_PM_WARNING)
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isVGGripped(t_index)
                while (not gripped):
                    wait(0.1)
                    gripped = self.isVGGripped(t_index)
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("FGP vacuum grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    def vacuum_release(self, t_index, f_wait):
        '''
        Releases the grippers vacuum

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type f_wait: bool
        @param f_wait: wait for the release to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.fgp_vg_release(t_index)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("FGP vacuum release command timeout", DR_PM_WARNING)
                    break
            else:
                RET_OK
            return RET_FAIL
        else:
            return RET_OK

class SG(Device):
    '''
    This class is for controlling a soft gripper
    '''
    cb = None
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if an SG device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsSG = self.cb.cb_is_device_connected(t_index, SG_ID)
        if IsSG is False:
            tp_popup("No Soft Gripper connected on the given instance", DR_PM_WARNING)
            return False
        else:
            return True

    #Is our Soft gripper initialized?
    def isInit(self, t_index):
        '''
        Returns with True if the SG device is properly initialized

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if initalized, False otherwise
        @rtype: bool
        '''
        return self.cb.sg_get_initialized(t_index)

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

        all_var = self.cb.sg_get_all_variables(t_index)
        return all_var["busy"]


    def init(self, t_index, tool_id):
        '''
        Intialize the gripper with the given tool id

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param tool_id: Tool id to be initalized with (1,2,3)
        @type tool_id: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        res = self.cb.sg_initialize(t_index, int(tool_id))

        #Wait for init
        tim_cnt = 0
        fbusy = self.isBusy(t_index)
        while (fbusy):
            wait(0.1)
            fbusy = self.isBusy(t_index)
            tim_cnt += 1
            if tim_cnt > 40:
                tp_popup("Soft gripper init command timeout", DR_PM_WARNING)
                break
        else:
            if res != 0:
                tp_popup("Failed to initialize Soft Gripper", DR_PM_WARNING)
                return RET_FAIL
            else:
                wait(2)
                return RET_OK

        return RET_FAIL

    def halt(self, t_index):
        '''
        Stop the grippers movement

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.sg_stop(t_index)

    def home(self, t_index):
        '''
        Sends the gripper to it's home position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        self.cb.sg_home(t_index)

    def get_max_depth(self, t_index):
        '''
        Returns with current maximum depth

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum depth in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.sg_get_depth_static_silicone(t_index)

    def get_width(self, t_index):
        '''
        Returns with current width

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Width in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.sg_get_width(t_index)

    def get_depth(self, t_index):
        '''
        Returns with current depth

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Depth in mm
        @rtype: float
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.sg_get_depth(t_index)

    def get_min_max(self, t_index):
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        return self.cb.sg_get_min_max(t_index)

    def get_max_open(self, t_index):
        '''
        Returns with current maximum width where the gripper can open

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Maximum width in mm
        @rtype: float
        '''
        limits = self.get_min_max(t_index)
        if limits == RET_FAIL:
            return RET_FAIL

        return limits["max_open"]

    def get_min_open(self, t_index):
        '''
        Returns with current mimimum width where the gripper can open

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: Minimum width in mm
        @rtype: float
        '''
        limits = self.get_min_max(t_index)
        if limits == RET_FAIL:
            return RET_FAIL

        return limits["min_open"]

    def grip(self, t_index, t_width, f_wait):
        '''
        Starts a normal grip command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_width: The diameter to move the gripper to in mm's
        @type t_width: float
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        #Sanity check
        limits = self.get_min_max(t_index)
        max_w = limits["max_open"]
        min_w = limits["min_open"]

        if ((t_width > max_w) or (t_width < min_w)):
            tp_popup("Invalid parameter for Soft Gripper width, valid range is: "+ str(min_w) +" - " + str(max_w), DR_PM_WARNING)
            return RET_FAIL

        #Call with no gentle grip and always True is_grip params
        self.cb.sg_grip(t_index, int(t_width), False, True)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("Soft gripper grip command timeout", DR_PM_WARNING)
                    break
            else:
                return RET_OK

            return RET_FAIL
        else:
            return RET_OK

    def gentle_grip(self, t_index, t_width, f_wait):
        '''
        Starts a gentle grip command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param t_width: The diameter to move the gripper to in mm's
        @type t_width: float
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Check init state
        if self.isInit(t_index) is False:
            tp_popup("Soft Gripper is not initalized! Initialize first!", DR_PM_WARNING)
            return RET_FAIL

        #Sanity check
        limits = self.get_min_max(t_index)
        max_w = limits["max_open"]
        min_w = limits["min_open"]

        if ((t_width > max_w) or (t_width < min_w)):
            tp_popup("Invalid parameter for Soft Gripper width, valid range is: "+ str(min_w) +" - " + str(max_w), DR_PM_WARNING)
            return RET_FAIL

        #Call with gentle grip and always True is_grip params
        self.cb.sg_grip(t_index, int(t_width), True, True)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("Soft gripper grip command timeout", DR_PM_WARNING)
                    break
            else:
                return RET_OK

            return RET_FAIL
        else:
            return RET_OK



class MG():
    '''
    This class is for handling the MG device
    '''
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if an MG device is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsMG = self.cb.cb_is_device_connected(t_index, MG_ID)
        if IsMG is False:
            tp_popup("No MG device connected on the given instance", DR_PM_WARNING)
            return False
        else:
            return True

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
        busyFlag = self.cb.mg_get_busy(t_index)
        return busyFlag

    def isNear(self, t_index):
        '''
        Gets if a workpiece is in close proximity or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if workpiece is detected, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        nearFlag = self.cb.mg_part_near(t_index)
        return nearFlag

    def isSmart(self, t_index):
        '''
        Gets if smart grip is available for the current configuration

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if smart grip is available, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        isSmartAvail = self.cb.mg_smart_grip_available(t_index)
        return isSmartAvail

    def isDropped(self, t_index):
        '''
        Gets if a part was dropped

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if a workpiece was dropped, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        isDropped = self.cb.mg_get_part_dropped(t_index)
        return isDropped

    def isStrengthNotReached(self, t_index):
        '''
        Gets if the MG could reach the desired magnetic srtength

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if strength is NOT, False is strength IS reached
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        StrNotReached = self.cb.mg_get_magnet_strength_not_reached(t_index)
        return StrNotReached

    def get_finger_type(self, t_index):
        '''
        Gets the current finger type

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: The current finger type
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        allVar = self.cb.mg_get_all_variables(t_index)
        if len(allVar) > 1:
            fingerType = allVar["finger_type"]
            return fingerType
        else:
            return RET_FAIL

    def get_finger_height(self, t_index):
        '''
        Gets the current finger height

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: float
        @return: The finger height in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        fingerHeight = self.cb.mg_get_finger_height_mm(t_index)
        return fingerHeight

    def get_strength_percent(self, t_index):
        '''
        Gets the reached magnetic strength

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Reached magnetic strength in %
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        currStrength = self.cb.mg_get_magnet_strength_percent(t_index)
        return currStrength

    def get_error(self, t_index):
        '''
        Gets the error code of the device

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: int
        @return: Error code of the device, 0 means no error
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        currError = self.cb.mg_get_error_code(t_index)
        return currError

    def auto_calibrate(self, t_index):
        '''
        Starts the auto calibration process of the magnetic gripper\n
        Could take up to 3 minutes\n
        No workpiece should be in a 9mm vicinity!

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int

        @rtype: bool
        @return: True if calibration was succesfull, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        #Release the MG
        self.release(t_index, True)

        self.cb.mg_auto_calibrate(t_index)

        tim_cnt = 0
        fbusy = self.isBusy(t_index)
        while (fbusy):
            wait(0.1)
            fbusy = self.isBusy(t_index)
            tim_cnt += 1
            if tim_cnt > 1800:
                tp_popup("Magnetic gripper auto calibration timed out", DR_PM_WARNING)
                break
        else:
            #Release after AC
            self.release(t_index, True)
            return RET_OK

        return RET_FAIL

    def set_protective_pad(self, t_index):
        '''
        Set pad tpye to protective pad

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.mg_set_finger_settings(t_index, 1, 0.4)

    def set_no_pad(self, t_index):
        '''
        Set pad tpye to NO pad

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.mg_set_finger_settings(t_index, 1, 0.0)

    def set_custom_pad(self, t_index, pad_height):
        '''
        Set pad tpye to custom height pad

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param pad_height: custom pad height in mm
        @type pad_height: int
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.mg_set_finger_settings(t_index, 3, float(pad_height))

    def grip(self, t_index, strength, f_wait):
        '''
        Starts a normal grip command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param strength: The desired magnetic strength in % (1-100)
        @type strength: int
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.mg_grip(t_index, int(strength), False)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("Magnetic gripper grip command timeout", DR_PM_WARNING)
                    break
            else:
                if self.isStrengthNotReached(t_index) is True:
                    tp_popup("The desired magnetic strength was not reached", DR_PM_WARNING)
                    return RET_FAIL
                else:
                    return RET_OK

            return RET_FAIL
        else:
            return RET_OK


    def smart_grip(self, t_index, strength, f_wait):
        '''
        Starts a smart grip command
        Smart grip checks for workpiece presence before activating magnets

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @param strength: The desired magnetic strength in % (1-100)
        @type strength: int
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR
        if self.isSmatAvailable(t_index) is False:
            tp_popup("Smart grip is unavailable on the chosen device", DR_PM_WARNING)
            return RET_FAIL

        self.cb.mg_grip(t_index, int(strength), True)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("Magnetic gripper smart grip command timeout", DR_PM_WARNING)
                    break
            else:
                if self.isStrengthNotReached(t_index) is True:
                    tp_popup("The desired magnetic strength was not reached", DR_PM_WARNING)
                    return RET_FAIL
                else:
                    return RET_OK

            return RET_FAIL
        else:
            return RET_OK

    def release(self, t_index, f_wait):
        '''
        Starts a release command, magnetic strength will be zero

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type f_wait: bool
        @param f_wait: wait for the move to end or not?
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        self.cb.mg_release(t_index)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy(t_index)
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy(t_index)
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("Magnetic gripper release command timeout", DR_PM_WARNING)
                    break
            else:
                if self.get_strength_percent(t_index) != 0:
                    tp_popup("The release failed to decrease magnet strength to 0%", DR_PM_WARNING)
                    return RET_FAIL
                else:
                    return RET_OK

            return RET_FAIL
        else:
            return RET_OK



class SDR():
    '''
    This class is for handling the Sander device
    '''
    cb = None

    def __init__(self, dev):
        #Mask for power supply warning
        self.PS_MASK = 0x20
        self.cb = dev.getCB()

    def isconn(self):
        '''
        Returns with True if a Sander device is connected, False otherwise

        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsSDR = self.cb.cb_is_device_connected(0, SDR_ID)
        if IsSDR is False:
            tp_popup("No Sander device connected", DR_PM_WARNING)
            return False
        else:
            #Check power supply
            warn_field = self.cb.sdr_get_warning(0)
            ps_f = warn_field and self.PS_MASK
            if ps_f != 0:
                tp_popup("Sander external power supply is not connected!", DR_PM_WARNING)
                return False
            else:
                return True

    def get_warning(self):
        '''
        Returns with warning code of the Sander

        @return: Warning code, 0 means no warnings
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_warning(0)

    def isRunning(self):
        '''
        Returns with True if the Sander is running

        @return: True if motor is running, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_motor_running(0)

    def isRampingUp(self):
        '''
        Returns with True if the Sander is ramping up

        @return: True if motor is ramping up, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_motor_ramping_up(0)

    def isRampingDown(self):
        '''
        Returns with True if the Sander is ramping down

        @return: True if motor is ramping down, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_motor_ramping_down(0)

    def isStopped(self):
        '''
        Returns with True if the Sander is stopped

        @return: True if motor is stopped, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_motor_stopped(0)

    def isBtnPressed(self):
        '''
        Returns with True if the Sander button is pressed

        @return: True if button is pressed, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_button_pressed(0)

    def getTemp(self):
        '''
        Returns with the current temperature of the Sander

        @return: Temperature in Celsius
        @rtype: float
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_current_temp_c(0)

    def getRPM(self):
        '''
        Returns with the current rotational speed of the Sander

        @return: Speed in RPM
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.sdr_get_current_rpm(0)


    def setRPM(self, setRPM, f_wait):
        '''
        Starts or stops the Sander

        @param setRPM: The desired Speed of the sander\n
        1000-10000 Starts the Sander at the given RPM, anything below 1000 stops the Sander
        @type setRPM: int (0-10000)
        @type f_wait: bool
        @param f_wait: wait for the command to end or not?
        '''
        if self.isconn() is False:
            return CONN_ERR

        if setRPM < 0 or setRPM > 10000:
            tp_popup("Invalid parameter for Sander RPM, 0-10000 is the valid range", DR_PM_WARNING)
            return RET_FAIL

        # Under 1000 rpm we will stop the sander
        if setRPM >= 1000 and setRPM <= 10000:

            self.cb.sdr_start(0, int(setRPM))

            if f_wait:
                #Wait for motor on
                tim_cnt = 0
                mot_on = self.isRunning()
                while (not mot_on):
                    wait(0.1)
                    mot_on = self.isRunning()
                    tim_cnt += 1
                    if tim_cnt > 30:
                        tp_popup("Sander start command timeout", DR_PM_WARNING)
                        break
                else:
                    #Motor is running
                    #Wait for ramp up and ramp down to go clear (running in valid range)
                    tim_cnt = 0
                    r_up = self.isRampingUp()
                    r_d = self.isRampingDown()
                    while ((not r_up) and (not r_d)):
                        r_up = self.isRampingUp()
                        r_d = self.isRampingDown()
                        tim_cnt += 1
                        if tim_cnt > 30:
                            tp_popup("Sander start command timeout", DR_PM_WARNING)
                            break
                    else:
                        return RET_OK
                    #Ramp up/down timeout
                    return RET_FAIL
                #Motor running timeout
                return RET_FAIL
            else:
                return RET_OK

        elif setRPM < 1000:

            self.cb.sdr_stop(0)

            if f_wait:
                #Wait for stop
                tim_cnt = 0
                stopped = self.isStopped()
                while (not stopped):
                    stopped = self.isStopped()
                    tim_cnt += 1
                    if tim_cnt > 20:
                        tp_popup("Sander stop command timeout", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                #Motor stop timeout
                return RET_FAIL



class EYES():
    '''
    This calss is for communicating with the EYES system
    '''
    cb = None
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self):
        '''
        Returns with True if an EYE system is connected, False otherwise

        @return: True if connected, False otherwise
        @rtype: bool
        '''
        conn = self.cb.eye_is_connected()
        if conn:
            return True
        else:
            tp_popup("EYES system is not connected", DR_PM_WARNING)
            return False

    #Returns with the robots current position in a format that can be sent over XML-RPC
    def _get_curr_pose_dict(self):
        #Get current position from the robot
        curr_pos_tuple = get_current_posx()
        #Convert pos tuple to a dictionary for sending on XML-rpc
        pose_dict = { "x" : curr_pos_tuple[0][0],
            "y" : curr_pos_tuple[0][1],
            "z" : curr_pos_tuple[0][2],
            "rx" : curr_pos_tuple[0][3],
            "ry" : curr_pos_tuple[0][4],
            "rz" : curr_pos_tuple[0][5]
        }

        return pose_dict

    #Convert an XML-RPC struct into a robot pose
    def _dict_to_pose(self, pose_d):
        rob_pos = posx(pose_d['x'], pose_d['y'], pose_d['z'], pose_d['rx'], pose_d['ry'], pose_d['rz'])

        return rob_pos

    #Check if pose is zero
    #Arg1 pose dict
    #Retval Boolean
    def _check_zero_pose(self, pose):
        if pose['x'] == 0.0 and pose['y'] == 0.0 and pose['z'] == 0.0 and pose['rx'] == 0.0 and pose['ry'] == 0.0 and pose['rz'] == 0.0:
            return True
        else:
            return False

    #Inspect + locate
    def locate(self, task_id, validate):
        '''
        Runs the given EYES locate task and returns with the number of workpieces found

        @param task_id: The id of EYES task defined in the web client
        @type task_id: int
        @param validate: Validate the return value or not?
        @type validate: bool
        @return: Number of workpieces found
        @rtype: int
        '''
        #Run process
        if self.isconn() is False:
            return CONN_ERR

        pose_struct = self._get_curr_pose_dict()

        #Run task
        retval = self.cb.eye_run_process(int(task_id), pose_struct, EYES_DOOSAN_ID)

        if (retval == -1):
            retval = 0 #Zero objects found

        if validate is True:
            if (retval == 0):
                tp_popup("No workpiece found while running EYES task: " + str(task_id), DR_PM_WARNING)
            return retval

        return retval

    def inspect(self, task_id, validate):
        '''
        Runs the given EYES inspect task and returns with the number of workpieces found

        @param task_id: The id of EYES task defined in the web client
        @type task_id: int
        @param validate: Validate the return value or not?
        @type validate: bool
        @return: Number of workpieces found
        @rtype: int
        '''
        return self.locate(task_id, validate)

    #Get valid object (get next workpiece from eyes queue)
    def get_object(self, gripper_sel, mod_type):
        if self.isconn() is False:
            return CONN_ERR

        if gripper_sel not in [0,1,2]:
            tp_popup("Invalid gripper type parameter for EYES, 0,1,2 is valid only", DR_PM_WARNING)
            return RET_FAIL

        #Get position from EYES
        pose_dict = self.cb.eye_get_valid_object(gripper_sel, mod_type)

        if self._check_zero_pose(pose_dict) is True:
            tp_popup("Got invalid position during inspect or locate", DR_PM_WARNING)
            return RET_FAIL

        #Convert position into robot position
        obj_pos = self._dict_to_pose(pose_dict)

        return obj_pos

    def get_next_wp(self, gripper_sel, model_type):
        '''
        Gets the next workpiece's position must be run after inspect or locate

        @return: The position of the next workpiece that was found in robot coordinate system
        @rtype: posx position
        '''
        return self.get_object(gripper_sel, model_type)

    #Calibrate (only used for external mount)
    def ext_calib(self):
        '''
        Send the current position to the EYES system for external camera mount calibration
        '''
        if self.isconn() is False:
            return CONN_ERR

        pose_struct = self._get_curr_pose_dict()

        self.cb.eye_calibrate(pose_struct, EYES_DOOSAN_ID)

    #Get the remaining workpiece count
    def get_wp_count(self):
        '''
        Returns with the number of workpieces left, must be run after inspect or locate

        @return: Number of workpieces left
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.eye_get_workpiece_count()

    #Get the workpiece type
    def get_wp_type(self):
        '''
        Returns with the model type of the found workpiece

        @return: Model type of the workpiece
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.eye_get_workpiece_type()

    #Get the inspection result (0 invalid, 1 pass, 2 fail, -1 error)
    def get_insp_res(self):
        '''
        Returns with the result of the inspection task\n
        0 means invalid\n
        1 means pass\n
        2 means fail\n
        -1 means error during inspection\n

        @return: Inspection result
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.eye_get_workpiece_inspection_eval()

    #Get the inspection match  (0-100%, -1 error)
    def get_insp_match(self):
        '''
        Returns with the match percentage of the inspecton\n
        0-100% inspection match\n
        -1 error during inspection


        @return: Number of workpieces found
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.eye_get_workpiece_inspection_match_percentage()

    #Returns with the landmarks position in robot pose
    def get_landmark(self):
        '''
        Returns with the landmarks position in the robots coordinate system

        @return: Landmarks position
        @rtype: posx position
        '''
        if self.isconn() is False:
            return CONN_ERR

        pose_struct = self._get_curr_pose_dict()

        landmark_dict = self.cb.eye_landmark_orig(pose_struct, EYES_DOOSAN_ID)

        if self._check_zero_pose(landmark_dict) is True:
            tp_popup("Got invalid position during landmark query", DR_PM_WARNING)
            return RET_FAIL

        return self._dict_to_pose(landmark_dict)

    #Save camera view pose into the EYES system
    def set_cam_pos(self):
        '''
        Saves the current robot position in the camera
        '''
        if self.isconn() is False:
            return CONN_ERR

        pose_struct = self._get_curr_pose_dict()

        res = self.cb.eye_set_cameraview_pose(pose_struct, EYES_DOOSAN_ID)

        if not res:
            tp_popup("Failed to set camera view pose in EYES", DR_PM_WARNING)
            return RET_FAIL
        else:
            return RET_OK

    #Get already saved camera position based on task ID
    #Returns with doosan robot pose
    def get_cam_pos(self, t_ID):
        '''
        Gets the previously saved camera postion in robot coordinate

        @param t_ID: Task ID of the EYES system where the position was saved
        @rtype: posx position
        @return: Camera view position in robot coordinate system
        '''
        if self.isconn() is False:
            return CONN_ERR

        pose_dict = self.cb.eye_get_cameraview_pose(t_ID, EYES_DOOSAN_ID)

        if self._check_zero_pose(pose_dict) is True:
            tp_popup("Got invalid position as camera pose", DR_PM_WARNING)
            return RET_FAIL

        rob_pose = self._dict_to_pose(pose_dict)

        return rob_pose



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


class HEX():
    '''
    This class is to get hex data
    '''
    cb = None

    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self):
        '''
        Returns with True if a HEX sensor is connected, False otherwise

        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsHEXv2 = self.cb.cb_is_device_connected(HEX_INDEX, HEXV2_ID)
        IsHEXv3 = self.cb.cb_is_device_connected(HEX_INDEX, HEXV3_ID)
        if IsHEXv2 is False and IsHEXv3 is False:
            tp_popup("No HEX sensor connected to the system", DR_PM_WARNING)
            return False
        else:
            return True

    def IsHEXv2(self):
        '''
        Returns with True if the connected sensor is a HEX version 2, False otherwise

        @return: True if verson 2 sensor, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.cb_is_device_connected(HEX_INDEX, HEXV2_ID)

    def IsHEXv3(self):
        '''
        Returns with True if the connected sensor is a HEX version 3, False otherwise

        @return: True if verson 3 sensor, False otherwise
        @rtype: bool
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.cb_is_device_connected(HEX_INDEX, HEXV3_ID)

    #Return value is a dictionary indexed by the Force and Torque value names
    def get_force(self):
        '''
        Returns with a dictionary containing the current force data\n
        The dictionary is indexed with ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']

        @return: Current force data dictionary
        @rtype: dict
        '''
        if self.isconn() is False:
            return CONN_ERR

        #Init result dictionary
        force_dict = dict.fromkeys(['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])

        res = self.cb.hex_get_all_variables()

        force_dict['Fx'] = res['ft'][0]
        force_dict['Fy'] = res['ft'][1]
        force_dict['Fz'] = res['ft'][2]
        force_dict['Tx'] = res['ft'][3]
        force_dict['Ty'] = res['ft'][4]
        force_dict['Tz'] = res['ft'][5]

        return force_dict

    def get_status(self):
        '''
        Returns with the status code of the hex sensor

        @return: Status code
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        res = self.cb.hex_get_all_variables()

        return res["status"]

    def zero(self):
        '''
        Applies an offset that zeroes the sensor data
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.ft_bias(True)

    def unzero(self):
        '''
        Removes any offset that was applied before
        '''
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.ft_bias(False)


class RG2FT():
    '''
    This class is for handling the RG2FT device
    '''
    cb = None
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self):
        '''
        Returns with True if an RG2FT is connected, False otherwise

        @return: True if connected, False otherwise
        @rtype: bool
        '''
        IsRG2FT = self.cb.cb_is_device_connected(HEX_INDEX, RG2FT_ID)
        if IsRG2FT is False:
            tp_popup("No RG2FT device connected to the system", DR_PM_WARNING)
            return False
        else:
            return True

    #Private method
    def _get_all_var(self):
        if self.isconn() is False:
            return CONN_ERR

        return self.cb.rg2ft_get_all_variables()

    def get_left_hex(self):
        '''
        Returns with a dictionary containing the current force data of the left HEX sensor\n
        The dictionary is indexed with ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']

        @return: Current force data dictionary
        @rtype: dict
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        #Init result dictionary
        force_dict = dict.fromkeys(['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])

        force_dict['Fx'] = all_var['left_hex'][0]
        force_dict['Fy'] = all_var['left_hex'][1]
        force_dict['Fz'] = all_var['left_hex'][2]
        force_dict['Tx'] = all_var['left_hex'][3]
        force_dict['Ty'] = all_var['left_hex'][4]
        force_dict['Tz'] = all_var['left_hex'][5]

        return force_dict

    def get_right_hex(self):
        '''
        Returns with a dictionary containing the current force data of the right HEX sensor\n
        The dictionary is indexed with ['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz']

        @return: Current force data dictionary
        @rtype: dict
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        #Init result dictionary
        force_dict = dict.fromkeys(['Fx', 'Fy', 'Fz', 'Tx', 'Ty', 'Tz'])

        force_dict['Fx'] = all_var['right_hex'][0]
        force_dict['Fy'] = all_var['right_hex'][1]
        force_dict['Fz'] = all_var['right_hex'][2]
        force_dict['Tx'] = all_var['right_hex'][3]
        force_dict['Ty'] = all_var['right_hex'][4]
        force_dict['Tz'] = all_var['right_hex'][5]

        return force_dict

    def get_left_proxi(self):
        '''
        Returns with the left proximity sensor value

        @return: Proximity in mm
        @rtype: float
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['left_proxi']

    def get_right_proxi(self):
        '''
        Returns with the right proximity sensor value

        @return: Proximity in mm
        @rtype: float
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['right_proxi']

    def get_width(self):
        '''
        Returns with the width of the gripper

        @return: Width in mm
        @rtype: float
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['width']

    def get_status(self):
        '''
        Returns with the status code of the device

        @return: Status code
        @rtype: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['status']

    def isBusy(self):
        '''
        Gets if the gripper is busy or not

        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['busy']

    def isGripped(self):
        '''
        Gets if the gripper is gripping or not

        @rtype: bool
        @return: True if part gripped, False otherwise
        '''
        if self.isconn() is False:
            return CONN_ERR

        all_var = self._get_all_var()

        return all_var['grip_detected']

    def set_prox_offset(self, lprox, rprox):
        '''
        Apply the given offsets to the proximity sensor values

        @param lprox: Left proximity offet
        @param rprox: Right proximity offet
        @type lprox: int
        @type rprox: int
        '''
        if self.isconn() is False:
            return CONN_ERR

        #Sanity check
        if lprox > 120 or lprox < 0:
            tp_popup("Invalid parameter for left proximity, range is 0-120", DR_PM_WARNING)
            return RET_FAIL

        if rprox > 120 or rprox < 0:
            tp_popup("Invalid parameter for right proximity, range is 0-120", DR_PM_WARNING)
            return RET_FAIL

        self.cb.rg2ft_proxi_offsets(int(lprox), int(rprox))

    #Read the current proximity values and set them as offsets
    def set_prox_offset_curr(self):
        '''
        Applies the current proximity sensor values as offset
        '''
        if self.isconn() is False:
            return CONN_ERR

        lprox = self.get_left_proxi()
        rprox = self.get_right_proxi()

        self.cb.rg2ft_proxi_offsets(int(lprox), int(rprox))

    #Get the objects size between the fingers
    def get_obj_width(self):
        '''
        Returns with the objects with that it is in the gripper\n
        Calculated the following way: width - left proxi - right proxi
        '''
        if self.isconn() is False:
            return CONN_ERR

        lprox = self.get_left_proxi()
        rprox = self.get_right_proxi()
        width = self.get_width()

        return width - lprox - rprox

    def halt(self):
        '''
        Stops the grippers movement
        '''
        if self.isconn() is False:
            return CONN_ERR

        self.cb.rg2ft_grip_stop()

    def grip(self, width, force, f_wait):
        '''
        Starts a grip command

        @param width: The width to grip 0-100 mm
        @type width: int
        @param force: The force to grip width 0-40 N
        @type force: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn() is False:
            return CONN_ERR

        #Sanity check
        if width < 0 or width > 100:
            tp_popup("Invalid width for RG2FT grip, 0-100 valid only", DR_PM_WARNING)
            return RET_FAIL

        if force < 0 or force > 40:
            tp_popup("Invalid force for RG2FT grip, 0-40 valid only", DR_PM_WARNING)
            return RET_FAIL

        #Blocking and depth comp should be False?
        self.cb.rg2ft_grip(int(width), int(force), False, False)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy()
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy()
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("RG2FT grip timeout", DR_PM_WARNING)
                    break
            else:
                #Grip detection
                grip_tim = 0
                gripped = self.isGripped()
                while (not gripped):
                    wait(0.1)
                    gripped = self.isGripped()
                    grip_tim += 1
                    if grip_tim > 20:
                        tp_popup("RG2FT grip detection timeout", DR_PM_WARNING)
                        break
                else:
                    return RET_OK
                return RET_FAIL
            return RET_FAIL
        else:
            return RET_OK

    #No grip detection
    def move(self, width, f_wait):
        '''
        Starts a move command

        @param width: The width to grip 0-100 mm
        @type width: int
        @type f_wait: bool
        @param f_wait: wait for the grip to end or not?
        '''
        if self.isconn() is False:
            return CONN_ERR

        #Sanity check
        if width < 0 or width > 100:
            tp_popup("Invalid width for RG2FT grip, 0-100 valid only", DR_PM_WARNING)
            return RET_FAIL

        #Blocking and depth comp should be False?
        self.cb.rg2ft_grip(int(width), 40, False, False)

        if f_wait:
            tim_cnt = 0
            fbusy = self.isBusy()
            while (fbusy):
                wait(0.1)
                fbusy = self.isBusy()
                tim_cnt += 1
                if tim_cnt > 30:
                    tp_popup("RG2FT move timeout", DR_PM_WARNING)
                    break
            else:
                return RET_OK
            return RET_FAIL
        else:
            return RET_OK

class SD():
    '''
    This class is for handling the Screw driver
    '''
    cb = None

    def __init__(self, dev):
        #To turn on/off error handling for this instance (def: ON)
        self.err_h = [True, True, True]
        self.cb = dev.getCB()

    def isconn(self, t_index):
        '''
        Returns with True if Screw driver is connected, False otherwise

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if connected, False otherwise
        @rtype: bool
        '''
        isSDConn = self.cb.cb_is_device_connected(t_index, SD_ID)
        if not isSDConn:
            tp_popup("No Screw driver connected", DR_PM_WARNING)
            return False
        else:
            return True

    def setErrhON(self, t_index):
        '''
        Turns ON error handling for all screwdriver commands
        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        '''
        self.err_h[t_index] = True

    def setErrhOFF(self, t_index):
        '''
        Turns OFF error handling for all screwdriver commands
        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        '''
        self.err_h[t_index] = False

    def getErrh(self, t_index):
        '''
        Gets if error handling is turned ON or OFF for the given instance

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @return: True if error handling is turned on for this instance, False if turned off
        @rtype: bool
        '''
        return self.err_h[t_index]



    #Private function
    def _err_handler(self, t_index):
        '''
        Checks ant interprets command result and erro code

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @return: True if error, False otherwise
        @rtype: bool
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        err_code = self.cb.sd_get_error_code(t_index)
        cmd_result = self.cb.sd_get_command_results(t_index)

        init_err_mask = 0xF0
        retval = True

        #Check the error code
        if err_code != 0:
            if err_code & 0x04 != 0:
                tp_popup("Screw driver saftey circuit triggered", DR_PM_ALARM)
            if err_code & 0x08 != 0:
                tp_popup("Screw driver not calibrated", DR_PM_ALARM)

            init_err = err_code & init_err_mask

            #Check init errors
            if init_err == 0x10:
                tp_popup("Screw driver init error: Shank stall current not reached", DR_PM_ALARM)
            elif init_err == 0x20:
                tp_popup("Screw driver init error: No shank index mark found", DR_PM_ALARM)
            elif init_err == 0x30:
                tp_popup("Screw driver init error: Unable to home shank", DR_PM_ALARM)
            elif init_err == 0x40:
                tp_popup("Screw driver init error: Invalid shank index placement", DR_PM_ALARM)
            elif init_err == 0x50:
                tp_popup("Screw driver init error: No torque index mark found", DR_PM_ALARM)
            elif init_err == 0x60:
                tp_popup("Screw driver init error: Torque difference overflow", DR_PM_ALARM)
            elif init_err == 0x70:
                tp_popup("Screw driver init error: Index mark value has changed (clean encoder disk)", DR_PM_ALARM)

            if err_code & 0x100:
                tp_popup("Wrong Quick changer type for the Screw driver", DR_PM_ALARM)
            if err_code & 0x200:
                tp_popup("Wrong Power Supply Type for the screw driver", DR_PM_ALARM)
        else:
            #No error
            retval = False

        #Check command result
        cmd_res_msg = None
        if cmd_result != 0:
            retval = True
            #Interpret command result
            if cmd_result == 1:
                cmd_res_msg = "Unknown command"
            elif cmd_result == 2:
                cmd_res_msg = "Not screwing in"
            elif cmd_result == 3:
                cmd_res_msg = "Timeout waiting for torque"
            elif cmd_result == 4:
                cmd_res_msg = "Torque exceeded prematurely"
            elif cmd_result == 5:
                cmd_res_msg = "Unable to loosen screw"
            elif cmd_result == 6:
                cmd_res_msg = "Shank reached the end"
            elif cmd_result == 7:
                cmd_res_msg = "Shank obstructed during move"
            else:
                cmd_res_msg = "Unknown command result"

            tp_popup("Screwdriver command result: " + cmd_res_msg, DR_PM_ALARM)
        else:
            retval = False

        return retval


    def isBusy(self, t_index):
        '''
        Gets if the screw driver is busy or not

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        shank_busy = self.cb.sd_get_shank_busy(t_index)
        dev_busy = self.cb.sd_get_screwdriver_busy(t_index)

        if ((not shank_busy) and (not dev_busy)):
            return False
        else:
            return True

    def get_torque_grad(self, t_index):
        '''
        Gets the torque gradient result

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: float
        @return: Torque gradient
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.sd_get_torque_gradient(t_index)

    def get_shank_pos(self, t_index):
        '''
        Gets the current shank position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: float
        @return: Shank position in mm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.sd_get_shank_position(t_index)

    def get_force(self, t_index):
        '''
        Gets the current force

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: float
        @return: Current force in N
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.sd_get_force(t_index)

    def get_ach_torq(self, t_index):
        '''
        Gets the achieved torque

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: float
        @return: Achieved torque in Nm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.sd_get_achieved_torque(t_index)

    def get_curr_torq(self, t_index):
        '''
        Gets the current torque

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @rtype: float
        @return: Current torque in Nm
        '''
        if self.isconn(t_index) is False:
            return CONN_ERR

        return self.cb.sd_get_current_torque(t_index)

    def tighten(self, t_index, force, screw_len, torq, f_wait):
        '''
        Starts a screw tighten command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param force:  Screw in force in N (18-30)
        @type force: int
        @param screw_len: Screwing lenght in mm (0-35)
        @type screw_len: float
        @param torq: Screw in torque in Nm (0-5)
        @type torq: float
        @param f_wait: Wait for command to finish or not?
        @type f_wait: bool
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        if force < 18 or force > 30:
            tp_popup("Invalid force parameter for tighten command, valid range: 18-30", DR_PM_WARNING)
            return RET_FAIL

        if screw_len < 0.0 or screw_len > 35.0:
            tp_popup("Invalid screw length for tighten command, valid range: 0-35", DR_PM_WARNING)
            return RET_FAIL

        if torq < 0.0 or torq > 5.0:
            tp_popup("Invalid torque parameter for tighten command, valid range: 0-5", DR_PM_WARNING)
            return RET_FAIL

        self.cb.sd_tighten(t_index, int(force), float(screw_len), float(torq))

        timeout = False
        if f_wait:
            busy_cnt = 0
            f_busy = self.isBusy(t_index)
            while (f_busy):
                wait(0.1)
                f_busy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 300:
                    tp_popup("Screw driver tighten command timeout", DR_PM_WARNING)
                    timeout = True
                    break
            else:
                timeout = False

        #Check for error
        if self.err_h[t_index]:
            err_state = self._err_handler(t_index)
            #There was no error and no timeout
            if (err_state == False) and (timeout == False):
                return RET_OK
            else:
                return RET_FAIL
        #There was no error handling only check timeout
        else:
            if timeout:
                return RET_FAIL
            else:
                return RET_OK

    def loosen(self, t_index, force, screw_len, f_wait):
        '''
        Starts a screw loosening command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param force:  Screw loosen force in N (18-30)
        @type force: int
        @param screw_len: Length of the screw in mm (0-35)
        @type screw_len: float
        @param f_wait: Wait for command to finish or not?
        @type f_wait: bool
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        if force < 18 or force > 30:
            tp_popup("Invalid force parameter for loosen command, valid range: 18-30", DR_PM_WARNING)
            return RET_FAIL

        if screw_len < 0.0 or screw_len > 35.0:
            tp_popup("Invalid screw length for loosen command, valid range: 0-35", DR_PM_WARNING)
            return RET_FAIL

        self.cb.sd_loosen(t_index, int(force), float(screw_len))

        timeout = False
        if f_wait:
            busy_cnt = 0
            f_busy = self.isBusy(t_index)
            while (f_busy):
                wait(0.1)
                f_busy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 100:
                    tp_popup("Screw driver loosen command timeout", DR_PM_WARNING)
                    timeout = True
                    break
            else:
                timeout = False

        #Check for error
        if self.err_h[t_index]:
            err_state = self._err_handler(t_index)
            #There was no error and no timeout
            if (err_state == False) and (timeout == False):
                return RET_OK
            else:
                return RET_FAIL
        #There was no error handling only check timeout
        else:
            if timeout:
                return RET_FAIL
            else:
                return RET_OK

    def pickup_screw(self, t_index, zforce, screw_len, f_wait):
        '''
        Starts a screw pickup command

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param zforce:  Screw pickup force in N (18-30)
        @type zforce: int
        @param screw_len: Length of the screw in mm (0-35)
        @type screw_len: float
        @param f_wait: Wait for command to finish or not?
        @type f_wait: bool
        '''

        #Sanity check
        if zforce < 18 or zforce > 30:
            tp_popup("Invalid zforce parameter for pickup screw command, valid range: 18-30", DR_PM_WARNING)
            return RET_FAIL

        if screw_len < 0.0 or screw_len > 35.0:
            tp_popup("Invalid screw length for pickup screw command, valid range: 0-35", DR_PM_WARNING)
            return RET_FAIL

        self.cb.sd_pickup_screw(t_index, int(zforce), float(screw_len))

        timeout = False
        if f_wait:
            busy_cnt = 0
            f_busy = self.isBusy(t_index)
            while (f_busy):
                wait(0.1)
                f_busy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 100:
                    tp_popup("Screw driver tighten command timeout", DR_PM_WARNING)
                    timeout = True
                    break
            else:
                timeout = False

        #Check for error
        if self.err_h[t_index]:
            err_state = self._err_handler(t_index)
            #There was no error and no timeout
            if (err_state == False) and (timeout == False):
                return RET_OK
            else:
                return RET_FAIL
        #There was no error handling only check timeout
        else:
            if timeout:
                return RET_FAIL
            else:
                return RET_OK

    def move_shank(self, t_index, shank_pos, f_wait):
        '''
        Moves the shank to the given position

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        @param shank_pos:  Shank position in mm (0-55)
        @type shank_pos: int
        @param f_wait: Wait for command to finish or not?
        @type f_wait: bool
        '''

        if self.isconn(t_index) is False:
            return CONN_ERR

        #Sanity check
        if shank_pos < 0 or shank_pos > 55:
            tp_popup("Invalid shank position parameter for move shank command, valid range: 0-55", DR_PM_WARNING)
            return RET_FAIL

        self.cb.sd_move_shank(t_index, int(shank_pos))

        timeout = False
        if f_wait:
            busy_cnt = 0
            f_busy = self.isBusy(t_index)
            while (f_busy):
                wait(0.1)
                f_busy = self.isBusy(t_index)
                busy_cnt += 1
                if busy_cnt > 30:
                    tp_popup("Screw driver move shank command timeout", DR_PM_WARNING)
                    timeout = True
                    break
            else:
                timeout = False

        #Check for error
        if self.err_h[t_index]:
            err_state = self._err_handler(t_index)
            #There was no error and no timeout
            if (err_state == False) and (timeout == False):
                return RET_OK
            else:
                return RET_FAIL
        #There was no error handling only check timeout
        else:
            if timeout:
                return RET_FAIL
            else:
                return RET_OK


    def halt(self, t_index):
        '''
        Stops the Screw driver

        @param t_index: The position of the device (0 for single, 1 for dual primary, 2 for dual secondary)
        @type t_index: int
        '''

        self.cb.sd_stop(t_index)

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


class LIFT():
    '''
    This class is for handling the LIFT device
    '''
    def __init__(self, dev):
        self.cb = dev.getCB()

    def isconn(self):
        '''
        Returns with True if LIFT is connected, False otherwise

        @return: True if connected, False otherwise
        @rtype: bool
        '''
        isLIFTConn = self.cb.cb_is_device_connected(LIFT_INDEX, LIFT_ID)
        if not isLIFTConn:
            tp_popup("No LIFT connected", DR_PM_WARNING)
            return False
        else:
            return True

    def _get_err_register(self):
        '''
        Gets the current error code of the LIFT

        @rtype: int
        @return: Current error register value
        '''
        if self.isconn() is False:
            return CONN_ERR
        lift_error = self.cb.lift_get_error()

        return lift_error

    def isBusy(self):
        '''
        Gets if the LIFT is busy or not

        @rtype: bool
        @return: True if busy, False otherwise
        '''
        if self.isconn() is False:
            return CONN_ERR
        busyFlag = self.cb.lift_get_busy()
        return busyFlag


    def get_pos(self):
        '''
        Gets the current position of the lift

        @rtype: float
        @return: Current position of the lift in mm
        '''
        if self.isconn() is False:
            return CONN_ERR
        liftpos = self.cb.lift_get_position()
        return liftpos

    def get_speed(self):
        '''
        Gets the current speed of the lift

        @rtype: float
        @return: Current position of the lift in mm
        '''
        if self.isconn() is False:
            return CONN_ERR
        liftspeed = self.cb.lift_get_speed()
        return liftspeed

    def get_error(self):
        '''
        Gets the current error code of the LIFT

        @rtype: int
        @return: Current error code
        '''
        lift_error = self._get_err_register()

        #Mask out ESTOP bit
        lift_error = lift_error & 0xfffe

        return lift_error

    def isESTOP(self):

        err_field = self._get_err_register()

        if (err_field & 0x01) != 0:
            return True
        else:
            return False

    def isInit(self):
        '''
        Gets if the LIFT is initialized or not

        @rtype: bool
        @return: True if initialized, False otherwise
        '''
        if self.isconn() is False:
            return CONN_ERR
        error_field = self.get_error()

        #Encoder mismatch is bit 3, if it's on then not inited
        if (error_field & (1<<3) == 0):
            return True
        else:
            return False

    def init(self):
        '''
        Sends a command that will initialize the device.
        The lift will move all the way down.
        '''
        if self.isconn() is False:
            return CONN_ERR
        #Check for ESTOP
        if self.isESTOP() == True:
            tp_popup("Lift is in Emergency Stop state", DR_PM_WARNING)
            return RET_FAIL

        #Call init
        self.cb.lift_initialize()
        wait(0.1)

        #Wait for init
        tim_cnt = 0
        busy_f = self.isBusy()
        while (busy_f):
            wait(0.1)
            busy_f = self.isBusy()
            tim_cnt += 1
            if tim_cnt > 2000:
                tp_popup("Lift init command timeout", DR_PM_WARNING)
                break
        else:
            #Check for ESTOP and errors
            if (self.isESTOP() != False):
                tp_popup("Lift is in Emergency Stop state", DR_PM_WARNING)
                return RET_FAIL
            else:
                if (self.get_error() != 0):
                    tp_popup("Lift error during init", DR_PM_WARNING)
                    return RET_FAIL
                else:
                    return RET_OK
        return RET_FAIL

    def halt(self):
        '''
        Stops the lift
        '''
        if self.isconn() is False:
            return CONN_ERR

        self.cb.lift_stop()

    def move(self, trg_pos, trg_speed):
        '''
        Moves the lift to the target position with the target speed

        @type trg_pos: float
        @param trg_pos: target position to move to (0-900 mm)
        @type trg_speed: float
        @param trg_speed: target speed to move with (1-100 mm/s)
        '''

        if self.isconn() is False:
            return CONN_ERR

        #Check for initialized
        if self.isInit() != True:
            tp_popup("Lift is not initialized", DR_PM_WARNING)
            return RET_FAIL

        #Check for ESTOP
        if self.isESTOP() != False:
            tp_popup("Lift is in Emergency Stop state", DR_PM_WARNING)
            return RET_FAIL

        curr_pos = self.get_pos()
        lift_err = self.get_error()

        if abs(curr_pos - trg_pos) <= 1:
            #Already at pos
            return RET_OK
        if (lift_err != 0):
            tp_popup("Lift is in error state", DR_PM_WARNING)
            return RET_FAIL

        try_cnt = 0

        while ((abs(curr_pos - trg_pos) > 1)):
            self.cb.lift_move(float(trg_pos), float(trg_speed))
            wait(0.1)
            tim_cnt = 0
            busy_f = self.isBusy()
            #Wait for busy
            while (busy_f):
                wait(0.1)
                busy_f = self.isBusy()
                tim_cnt += 1
                if tim_cnt > 1500:
                    tp_popup("Lift move command timeout", DR_PM_WARNING)
                    return RET_FAIL
            #Wait for ESTOP
            tim_cnt = 0
            estop_f = self.isESTOP()
            while (estop_f):
                wait(0.1)
                estop_f = self.isESTOP()
                tim_cnt += 1
                if tim_cnt > 100:
                    tp_popup("Lift IS in Emergency Stop state", DR_PM_WARNING)
                    return RET_FAIL
            #Update pos, err and try_cnt
            curr_pos = self.get_pos()
            try_cnt += 1
            if (try_cnt > 3):
                tp_popup("Lift didn't move in 3 tries", DR_PM_WARNING)
                return RET_FAIL
        return RET_OK

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

or_vgx = VG(or_dev)
or_rgx = RG(or_dev)
or_tfg = THREEFG(or_dev)
or_2fg = TWOFG(or_dev)
or_eyes = EYES(or_dev)
or_sg = SG(or_dev)
or_mg = MG(or_dev)
or_sdr = SDR(or_dev)
or_vgp = VGP(or_dev)
or_hex = HEX(or_dev)
or_rg2ft = RG2FT(or_dev)
or_sd = SD(or_dev)
or_fgp = FGP(or_dev)
or_lift = LIFT(or_dev)
or_cb = CBIO(or_dev)
or_wl = Weblytics(or_dev)



