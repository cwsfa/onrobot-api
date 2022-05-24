#!/usr/bin/env python

#OnRobot library for Doosan robots
#Version: Ver 5.15.0

import zlib, base64
def convert(data):
    decoded64 = base64.b64decode(data)
    final = zlib.decompress(decoded64)
    with open('api_original.py', mode='w') as f:
        f.write(final.decode("utf-8"))
    print('Done')

if __name__ == "__main__":
    with open('api_binary.txt', mode='r') as f:
        data = f.read()
    convert(data)
    print("Conversion from binary to a python script completed!")