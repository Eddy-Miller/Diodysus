'''
README:
Questo script legge i dati dal sensore e li invia tramite UDP su una porta specifica.
Al momento i dati sono generati casualmente
I token sono letti dal file token.txt (non sincronizzato con GIT)
IR non ancora implementate
'''


#import
from asyncio import sleep
import random, socket, os , sys, time
import time
import serial
import csv, piir

#global variable and costants
MODE_LIST = ["ethernet", "serial", "infrared"]
#dictionary with token:sensor_name entry (load from file token.txt)
token_dict = {}



#comunication functions
def ethernet_mode(ethernet_address,ethernet_port):
    print("Ethernet mode - using plain one-way UDP")
    print("Press Ctrl+C to exit")
    
    #UDP socket setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        #reading data from the sensors
        msg = random_sensor_value()
        #send message
        msg = str(msg)
        sock.sendto(msg.encode(), (ethernet_address, ethernet_port) )
        print("Sent: {}, to {}:{}".format(msg, ethernet_address, ethernet_port))
        #wait for a while
        time.sleep(10)

def serial_mode():
    print("Serial mode - using serial module")
    print("Press Ctrl+C to exit")

    #instantiate a Serial object, used for sending data to the serial port
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
        print(counter)
        time.sleep(1) 
        counter += 1


def infrared_mode():
    print("Infrared mode - reliability not guaranteed")
    print("WARNING: IR hardware must used in dark environment")
    print("Press Ctrl+C to exit")
    #instantiate the piir class and start the loop (at the moment we don't know what light.json file is)
    remote = piir.Remote('light.json', 17)

    #TODO DA TESTARE SE POSSIBILE INVIARE TOKEN IN AMBIENTE CON POCHE INTERFERENZE

    while True:
        #read the sensor value
        msg = random_sensor_value()

        #create the message to send (in string format)
        msg_to_send = str(msg["sensor_name"]) + "," + str(msg["sensor_value"])
        print(msg)
        #remote.send_data(bytes(msg_to_send["sensor_token"], 'utf-8'))
        remote.send_data(bytes(msg_to_send, 'utf-8'))
        time.sleep(5)

#utility functions
def random_sensor_value():
    msg = {"sensor_token":"token_placeholter", "sensor_name": "sensor_name_placeholder", "sensor_value": "sensor_value_placeholder" }

    tokenList = list(token_dict.keys())
    token = random.choice(tokenList)

    msg["sensor_token"] = token
    msg["sensor_value"] = random.randint(0, 100)
    msg["sensor_name"] = token_dict[token]

    return msg

#return a dictionary with "token":"sensor_name" entry based on file token.txt (but it's a CSV file)
#token is the first column of the CSV file with column token,sensor_name
def load_token_dict_from_file():
    with open('token.txt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        print("Sensors list:")
        for row in csv_reader:
            token_dict[row[0]] = row[1]
            print(f'\tSensor token: {row[0]} Sensor Name: {row[1]}')
    return token_dict


def main():

    #ip address and port for ethernet mode
    ethernet_address = "localhost"
    ethernet_port = 50000

    #reading token list from file
    token_dict = load_token_dict_from_file()


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