#!/usr/bin/env python3

import xmlrpc.client

class Device:
    '''
    Generic device object
    '''
    cb = None

    def __init__(self):
        #try to get Computebox IP address
        try:
            self.Global_cbip = '192.168.1.1'
        except NameError:
            print("Global_cbip is not defined!")

    def getCB(self):
            try:
                self.cb = xmlrpc.client.ServerProxy(
                    "https://" + str(self.Global_cbip) + ":41414/")
                return self.cb
            except TimeoutError:
                print("Connection to ComputeBox failed!")

    def report_robot(self):
        if self.cb is not None:
            #Send our ID to the robot
            # self.cb.cb_report_robot_type(EYES_DOOSAN_ID)
            print('Report robot completed!')
            pass


if __name__ == "__main__":
    or_dev = Device()
    or_dev.getCB()
    or_dev.report_robot()
