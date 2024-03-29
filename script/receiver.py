'''
README:
Legge i dati ricevuti dal RASP A e li invio a Thingsboard usando le API REST

Ethernet mode:
legge da socket UDP e costruisce un JSON per ogni messaggio 

'''

#import
import random, socket, os , sys, time, json, requests

import time, csv
from time import sleep
import serial
from curses import keyname
from piir.io import receive
from piir.decode import decode
import hashlib
  


from piir.prettify import prettify


#global variable and costants
MODE_LIST = ["ethernet", "serial", "infrared"]

#thingsboard parameters
tb_protocol = "http"
tb_port = "8080"
tb_address = "localhost"

#infared sender pin config
INFRARED_PIN = 0

def config_pin():

    #open json file in read mode
    with open('config/conf_receiver.json', 'r') as f:
        data = json.load(f)

    #infared sender pin config
    global INFRARED_PIN
    INFRARED_PIN = data["infrared_sensor"]["INFRARED_PIN"]
    print(INFRARED_PIN)


#return a dictionary with "token":"sensor_name" entry based on file token.txt (but it's a CSV file)
#token is the first column of the CSV file with column token,sensor_name
token_dict = {}

def load_token_dict_from_file():
    with open('token.txt') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        print("Sensors list:")
        for row in csv_reader:
            token_dict[row[1]] = row[0]
            print(f'\tSensor token: {row[0]} Sensor Name: {row[1]}')
    return token_dict


#comunication functions
def ethernet_mode(ethernet_address, ethernet_port):
    print("Ethernet mode - using plain one-way UDP")
    print("Press Ctrl+C to exit")
    #UDP server socket setup
    serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #binding
    serversock.bind(("0.0.0.0", ethernet_port))
    print("UDP server up and listening on ethernet_port: {}\nCTRL+C to stop".format(ethernet_port))

    #Reading sensor token from file
    keys = {}
    token_dict = load_token_dict_from_file()

    #listening
    while True:
        #reading data from the UDP socket
        byteAddressPair = serversock.recvfrom(1024)
        message = byteAddressPair[0].decode()
        address= byteAddressPair[1]
        print("Received: {} from {}:{}".format(message, address[0], address[1]))
        
        #convert in JSON
        #replace ' with " in msg (for json.loads)
        message =message.replace("\'", '\"')
        message_json = json.loads(message)
        
        #reading thingboard token and remove it's key from the message
        token = token_dict[message_json["sensor_name"]]
        del message_json["sensor_token"]
       
        
        #send JSON to Thingsboard with HTTP REST API (using the utility function)
        rest_to_thingsboard(token,message_json)


def serial_mode():
    print("Serial mode - using serial module")
    print("Press Ctrl+C to exit")

    keys = {}
    token_dict = load_token_dict_from_file()

    ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    while True:
        x=ser.readline().decode("utf-8")  #readline (i wish that readline return an econoded UTF-8 string)
        
        message=x
        print("Received: {}".format(message))
        
        #convert in JSON
        #replace ' with " in msg (for json.loads)
        message =message.replace("\'", '\"')
        message_json = json.loads(message)
        
        #reading thingboard token and remove it's key from the message
        token = token_dict[message_json["sensor_name"]]
        del message_json["sensor_token"]

        #print(message_json)
       
        #send JSON to Thingsboard with HTTP REST API (using the utility function)
        rest_to_thingsboard(token,message_json) 

def infrared_mode():
    print("Infrared mode - reliability not guaranteed")
    print("WARNING: IR hardware must not be used under direct sunlight")
    print("Press Ctrl+C to exit")

    
    keys = {}
    token_dict = load_token_dict_from_file()
   
    while True:
        try:
           
            data = decode(receive(22))
            
            if data:
                

                keys['keyname'] = data

                #print (keys['keyname'])

                prettified_data =prettify(keys)
                #print (prettified_data["keys"]['keyname'])
                hex_data = prettified_data["keys"]['keyname']
                string_received = bytes.fromhex(hex_data).decode('utf-8')
                print("ricevuto"+string_received)
                
                string_array = string_received.split(sep=",")
                sensor_name = string_array[0]
                sensor_value = string_array[1]
                my_hash = string_array[2]
                
                #check hash
                string_da_verificare = sensor_name + "," + sensor_value
            
                # function 
                result = hashlib.md5(string_da_verificare.encode("utf-8"))
                result = str(result.digest())
                result = result[:5]
                # printing the equivalent byte value.
               
                if result == result:
                    #Hash verificato
                    print("Hash verified. sensor name: {}, sensor value {}".format(sensor_name,sensor_value) )
                    sensor_token = token_dict[sensor_name]

                    #Creazione del JSON
                    msg = {"sensor_name": sensor_name, "sensor_value": sensor_value}
                   

                    #send JSON to Thingsboard with HTTP REST API (using the utility function)
                    #reading thingboard token and remove it's key from the message
                  
                    rest_to_thingsboard(sensor_token,msg)
                else:
                    print("hash not verified")

                
        except Exception as e:
            print("Error: {}".format(e))
            print("Message not received")
            continue

#utility functions
def rest_to_thingsboard(token,message):
    
    #url building and HTTP header settings
    url = f"{tb_protocol}://{tb_address}:{tb_port}/api/v1/{token}/telemetry"
    header = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
   
    try:
        while True:
            #JSON conversion
            data_json = json.dumps(message)
            #HTTP request
            http_response = requests.post(url=url,data=data_json,headers=header)
            
            if http_response.status_code == 200:
                print(f"send data to ThingsBoard: {data_json}")
                return 0
    except requests.exceptions.ConnectionError as e:
        print("Request Exception", e)
    except KeyboardInterrupt:
     pass
    except Exception as e:
        print("General Exception: ", e)


def main():

    #ip address and port for ethernet mode
    ethernet_address = "192.168.10.12" #must set server ip address because this raspberry have two ip address. One for internet connection and the second is for connection with raspbian_a
    ethernet_port = 50000
    

    #check number of arguments equal to 2
    if len(sys.argv) != 2:
        print("Usage: python sender.py <mode>\nMode can be: ethernet, serial or infrared")
        sys.exit(1)
    
    #check if mode is valid
    if sys.argv[1] not in MODE_LIST:
        print("Invalid mode: {}\nMode can be: ethernet, serial or infrared".format(sys.argv[1]))
        sys.exit(1)
    
    mode = sys.argv[1]
    print("Hello World - I'm the receiver in mode: " + mode)

    #execute the current mode
    if(mode == "ethernet"):
        ethernet_mode(ethernet_address, ethernet_port)
    elif(mode == "serial"):
        serial_mode()
    elif(mode == "infrared"):
        infrared_mode()

if __name__ == "__main__":
    main()
