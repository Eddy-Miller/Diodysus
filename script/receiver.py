'''
README:
Legge i dati ricevuti dal RASP A e li invio a Thingsboard usando le API REST

Ethernet mode:
legge da socket UDP e costruisce un JSON per ogni messaggio 

TODO: il server UPD è sequenziale, quindi non è possibile gestire più richieste contemporaneamente
anche se si connette un solo client quindi può andare bene anche così

'''


#import
import random, socket, os , sys, time, json, requests

#global variable and costants
MODE_LIST = ["ethernet", "serial", "infrared"]

#thingsboard parameters
tb_protocol = "http"
tb_port = "8080"
tb_address = "localhost"


#comunication functions
def ethernet_mode(port):
    #UDP server socket setup
    serversock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #binding
    serversock.bind(('localhost', port))
    print("UDP server up and listening on port: {}\nCTRL+C to stop".format(port))

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

        #send JSON to Thingsboard with HTTP REST API (using the utility function)
        #TODO


def serial_mode():
    pass

def infrared_mode():
    pass

#utility functions
def rest_to_thingboard(token,message):
    #NON TESTATE
    url = f"{tb_protocol}://{tb_address}:{tb_port}/api/v1/{token}/telemetry"

    header = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

    
    try:
        #sending POST request
        http_response = requests.post(url=url,data=message,headers=header)

        if http_response.status_code == 200:
            print(f"send data to ThingsBoard: {message}")
          
        
    except requests.exceptions.ConnectionError as e:
        print("Request Exception", e)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("General Exception: ", e)


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

    #execute the current mode
    if(mode == "ethernet"):
        ethernet_mode(5555)
    elif(mode == "serial"):
        serial_mode()
    elif(mode == "infrared"):
        infrared_mode()

if __name__ == "__main__":
    main()