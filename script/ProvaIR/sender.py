import piir

remote = piir.Remote('light.json', 17)

while(True):
    input_data = input('Inserire testo: ')
    remote.send_data(bytes(input_data, 'utf-8'))
    print('Inviato: ' + input_data)


