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
from pickle import TRUE
import RPi.GPIO as GPIO
import time
import Adafruit_DHT as dht
import hashlib, json


#global variable and costants
MODE_LIST = ["ethernet", "serial", "infrared"]
#dictionary with token:sensor_name entry (load from file token.txt)
token_dict = {}

#distance sensor config
PIN_TRIGGER = 0
PIN_ECHO = 0

#infared sender pin config
INFRARED_PIN = 0

#DHT22 spin config
PIN_DHT22 = 0

#config pin for sensor
def config_pin():
    #load pin from conf_sender.json
    with open('conf_sender.json', 'r') as f:
        data = json.load(f)

    #DHT22 spin config
    PIN_DHT22 = data["DHT22_sensor"]["PIN_DHT22"]
    print(PIN_DHT22)

    #distance sensor config
    PIN_TRIGGER = data["distance_sensor"]["PIN_TRIGGER"]
    PIN_ECHO = data["distance_sensor"]["PIN_ECHO"]

    print(PIN_TRIGGER)
    print(PIN_ECHO)

    #infared sender pin config
    INFRARED_PIN = data["infrared_sensor"]["INFRARED_PIN"]
    print(INFRARED_PIN)
    

def createMessage():
    #read DHT22
    humidity, temperature = readDHT22()
    msgDHT22_temperature = {"sensor_token":"token_placeholter", "sensor_name": "sensor_name_placeholder", "sensor_temperature": "sensor_value_placeholder" }
    msgDHT22_temperature["sensor_name"] = "T"
    msgDHT22_temperature["sensor_value"] = int(temperature)

    msgDHT22_humidity = {"sensor_token":"token_placeholter", "sensor_name": "sensor_name_placeholder", "sensor_humidity": "sensor_value_placeholder" }
    msgDHT22_humidity["sensor_name"] = "H"
    msgDHT22_humidity["sensor_value"] = int(humidity)

    #read distance
    
    msgDistance = {"sensor_token":"token_placeholter", "sensor_name": "sensor_name_placeholder", "sensor_value": "sensor_value_placeholder" }
    msgDistance["sensor_name"] = "D"
    msgDistance["sensor_value"] = int(readDistance(PIN_TRIGGER, PIN_ECHO))

    return msgDHT22_temperature, msgDHT22_humidity, msgDistance



#definire la funzione per il sensore di temperatura e umidità
def readDHT22():
    print("Function readDHT22")
    #definire il pin del sensore DHT22
    DHT22_pin = PIN_DHT22 #GPIO12
    #definire il tipo di sensore DHT22
    DHT22_sensor = dht.DHT22
    print("Reading DHT22")
    humidity,temperature = dht.read_retry(DHT22_sensor, DHT22_pin)

    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        print("Failed to retrieve data from humidity sensor")
    
    return humidity, temperature
        
#GPIO setup fro distance sensor
def setupGPIO(PIN_TRIGGER, PIN_ECHO):
    
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)
    
    print("Waiting for sensor to settle")
    time.sleep(3)
    return 

def readDistance(PIN_TRIGGER, PIN_ECHO):
    GPIO_TRIGGER = PIN_TRIGGER
    GPIO_ECHO = PIN_ECHO
    
        # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2

    print("Distance: {:.2f} cm".format(distance))
    return distance
 
  

#comunication functions
def ethernet_mode(ethernet_address,ethernet_port):
    print("Ethernet mode - using plain one-way UDP")
    print("Press Ctrl+C to exit")
    
    #UDP socket setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        #reading data from the sensors
        msgDHT22_temperature, msgDHT22_humidity, msgDistance = createMessage()
        
        #encoding message
        msgDHT22_temperature = str(msgDHT22_temperature) + "\n"
        msgDHT22_humidity = str(msgDHT22_humidity) + "\n"
        msgDistance = str(msgDistance) + "\n"

        #send message
        sock.sendto(msgDHT22_temperature.encode(), (ethernet_address, ethernet_port) )
        sock.sendto(msgDHT22_humidity.encode(), (ethernet_address, ethernet_port) )
        sock.sendto(msgDistance.encode(), (ethernet_address, ethernet_port) )
        print("Sent: {}, to {}:{}".format(msgDHT22_temperature, ethernet_address, ethernet_port))
        time.sleep(1)
        print("Sent: {}, to {}:{}".format(msgDHT22_humidity, ethernet_address, ethernet_port))
        time.sleep(1)
        print("Sent: {}, to {}:{}".format(msgDistance, ethernet_address, ethernet_port))

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

    while True:
        #reading data from the sensors
        msgDHT22_temperature, msgDHT22_humidity, msgDistance = createMessage()

        #encoding message
        msgDHT22_temperature = str(msgDHT22_temperature) + "\n"
        msgDHT22_humidity = str(msgDHT22_humidity) + "\n"
        msgDistance = str(msgDistance) + "\n"
        msgDHT22_temperature = msgDHT22_temperature.encode()
        msgDHT22_humidity = msgDHT22_humidity.encode()
        msgDistance = msgDistance.encode()

        #send message
        ser.write(msgDHT22_temperature)
        ser.write(msgDHT22_humidity)
        ser.write(msgDistance)

        #print message sent
        print("Sent: {}".format(msgDHT22_temperature))
        time.sleep(1)
        print("Sent: {}".format(msgDHT22_humidity))
        time.sleep(1)
        print("Sent: {}".format(msgDistance))

        #wait for a while
        time.sleep(10) 


def infrared_mode():
    print("Infrared mode - reliability not guaranteed")
    print("WARNING: IR hardware must used in dark environment")
    print("Press Ctrl+C to exit")
    #instantiate the piir class and start the loop (at the moment we don't know what light.json file is)
    remote = piir.Remote('light.json', INFRARED_PIN)

    #TODO DA TESTARE SE POSSIBILE INVIARE TOKEN IN AMBIENTE CON POCHE INTERFERENZE

    while True:
        #reading data from the sensors
        msgDHT22_temperature, msgDHT22_humidity, msgDistance = createMessage()

        #send messages
        #temperture dictionary
        
        '''remote.send_data(bytes(msgDHT22_temperature["sensor_token"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(msgDHT22_temperature["sensor_name"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(str(msgDHT22_temperature["sensor_value"]), 'utf-8'))
        time.sleep(0.5)
        print("Sent: {}".format(msgDHT22_temperature))

        #humidity dictionary
        remote.send_data(bytes(msgDHT22_humidity["sensor_token"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(msgDHT22_humidity["sensor_name"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(str(msgDHT22_humidity["sensor_value"]), 'utf-8'))
        time.sleep(0.5)
        print("Sent: {}".format(msgDHT22_humidity))

        #distance dictionary
        remote.send_data(bytes(msgDistance["sensor_token"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(msgDistance["sensor_name"], 'utf-8'))
        time.sleep(0.5)
        remote.send_data(bytes(str(msgDistance["sensor_value"]), 'utf-8'))
        time.sleep(0.5)
        print("Sent: {}".format(msgDistance))'''

        str_msgDHT22_temperature = msgDHT22_temperature["sensor_name"]+","+ str(msgDHT22_temperature["sensor_value"])
        hash_str_msgDHT22_temperature = str(hashlib.md5(str_msgDHT22_temperature.encode()).hexdigest())
        remote.send_data(bytes(str_msgDHT22_temperature+","+hash_str_msgDHT22_temperature[:5], 'utf-8'))
        print("Sent: {}".format(str_msgDHT22_temperature+","+hash_str_msgDHT22_temperature[:5]))
        time.sleep(0.5)
        
        str_msgDHT22_humidity = msgDHT22_humidity["sensor_name"]+","+ str(msgDHT22_humidity["sensor_value"])
        hash_str_msgDHT22_humidity = str(hashlib.md5(str_msgDHT22_humidity.encode()).hexdigest())
        remote.send_data(bytes(str_msgDHT22_humidity+","+hash_str_msgDHT22_humidity[:5], 'utf-8'))
        print("Sent: {}".format(str_msgDHT22_humidity+","+hash_str_msgDHT22_humidity[:5]))
        time.sleep(0.5)

        str_msgDistance = msgDistance["sensor_name"]+","+ str(msgDistance["sensor_value"])
        hash_str_msgDistance = str(hashlib.md5(str_msgDistance.encode()).hexdigest())
        remote.send_data(bytes(str_msgDistance+","+hash_str_msgDistance[:5], 'utf-8'))
        print("Sent: {}".format(str_msgDistance+","+hash_str_msgDistance[:5]))
        time.sleep(0.5)
        #wait for a while
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
            token_dict[row[1]] = row[0]
            print(f'\tSensor token: {row[0]} Sensor Name: {row[1]}')
    return token_dict


def main():

        
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

    #ip address and port for ethernet mode
    ethernet_address = "192.168.10.12" #the local ip address of the receiver
    ethernet_port = 50000

    #reading token list from file
    token_dict = load_token_dict_from_file()
    print("token_dict: {}".format(token_dict))

    #GPIO setup for distance sensor
    setupGPIO(PIN_TRIGGER, PIN_ECHO)

    #config pin snesor
    config_pin()


    #set pin
    try:
        #setup the GPIO pins
        
       

        #execute the current mode
        if(mode == "ethernet"):
            ethernet_mode(ethernet_address, ethernet_port)
        elif(mode == "serial"):
            serial_mode()
        elif(mode == "infrared"):
            infrared_mode()
    finally:
        GPIO.cleanup()
    


if __name__ == "__main__":
    main()
