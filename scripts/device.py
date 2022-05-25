#!/usr/bin/env python3

import xmlrpc.client

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

if __name__ == '__main__':
    device = Device()
    device.getCB()
