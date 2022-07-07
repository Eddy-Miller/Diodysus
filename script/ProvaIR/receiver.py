from curses import keyname
from piir.io import receive
from piir.decode import decode

from piir.prettify import prettify
import json



keys = {}

while True:
    data = decode(receive(22))
    if data:
        keys['keyname'] = data

        #print (keys['keyname'])

        prettified_data =prettify(keys)
        print (prettified_data["keys"]['keyname'])
        hex_data = prettified_data["keys"]['keyname']
        string_name = bytes.fromhex(hex_data).decode('utf-8')
        print(string_name)
        
