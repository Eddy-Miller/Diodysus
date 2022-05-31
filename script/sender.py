'''
README:
Questo script legge i dati dal sensore e li invia tramite UDP su una porta specifica.
Al momento i dati sono generati casualmente
IR e seriale non ancora implementate
'''


#import
import random, socket, os , sys, time
import time
import serial

#global variable and costants
MODE_LIST = ["ethernet", "serial", "infrared"]



#comunication functions
def ethernet_mode(ethernet_address,ethernet_port):
    #UDP socket setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        #reading data from the sensors
        msg = random_sensor_value()
        #send message
        msg = str(msg)
        sock.sendto(msg.encode(), (ethernet_address, ethernet_port) )
        print("Sent: {}, to {}:{}".format(msg, ethernet_address, pethernet_portort))
        #wait for a while
        time.sleep(10)

def serial_mode():
    ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    counter=0
    while 1: 
        ser.write(str.encode(f'{counter}\n'))
        time.sleep(1) 
        counter += 1

def infrared_mode():
    pass

#utility functions
def random_sensor_value():
    msg = { "sensor_name": "sensor_name_placeholder", "sensor_value": "sensor_value_placeholder" }

    msg["sensor_value"] = random.randint(0, 100)
    msg["sensor_name"] ="random_value"

    return msg

def main():

    #ip address and port for ethernet mode
    ethernet_address = "localhost"
    ethernet_port = 5555


    #check number of arguments equal to 2
    if len(sys.argv) != 2:
        print("Usage: python sender.py <mode>\nMode can be: ethernet, serial or infrared")
        sys.exit(1)
    
    #check if mode is valid
    if sys.argv[1] not in MODE_LIST:
        print("Invalid mode: {}\nMode can be: ethernet, serial or infrared".format(sys.argv[1]))
        sys.exit(1)
    
    mode = sys.argv[1]
    print("Hello World - I'm the sender in mode: " + mode)

    #execute the current mode
    if(mode == "ethernet"):
        ethernet_mode(ethernet_address, ethernet_port)
    elif(mode == "serial"):
        serial_mode()
    elif(mode == "infrared"):
        infrared_mode()
    


if __name__ == "__main__":
    main()