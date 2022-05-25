#!/usr/bin/env python3

import zlib, base64

def convert(data):
    decoded64 = base64.b64decode(data)
    final = zlib.decompress(decoded64)
    with open('api_original.py', mode='w') as f:
        f.write(final.decode("utf-8"))
    print("Conversion from byte to a python script completed!")

if __name__ == "__main__":
    with open('api_byte.txt', mode='r') as f:
        data = f.read()
    convert(data)
