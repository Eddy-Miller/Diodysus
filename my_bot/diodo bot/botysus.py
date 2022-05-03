
import telepot
import time
from telepot.loop import MessageLoop
from pprint import pprint

def broadcast():
    with open("./regFile.txt", "a+") as f:
        f.seek(0)
        line=f.readline()
        while line != '':
            bot.sendMessage(line, "changed profile pic :)")
            line=f.readline()

def handle(msg):

    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    pprint(msg)

    username = msg['from']['username']
    user_id = msg['from']['id']
    
    if content_type == 'text':
        text = msg['text']

        if text == '/broadcast':
            broadcast()

        if text == '/register':
          
            with open("./regFile.txt", "a+") as f: #apre un file come try catch ed esegue comandi, alla fine lo chiude in automatico
                #f.write(os.linesp)
                #f.write(username)
                f.seek(0)
                line=f.readline()
                isRegistered = False
                while line != '':
                    if line == (str(chat_id)+"\n"): 
                        isRegistered = True
                    line=f.readline()
                if isRegistered == True:
                    bot.sendMessage(chat_id, "You are already registered.")
                else:
                    print(chat_id, file=f)
                    response = 'you are now registered to Diodysus!'
                    bot.sendMessage(chat_id, response)
                

    bot.sendMessage(chat_id, text)
    


TOKEN = '5311475211:AAH6zgzP7dDxqMmQ-UYhGMT7e-nRPQxXpuE'

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
