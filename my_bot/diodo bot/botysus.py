
import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import sqlite3
from io import StringIO
import time

class RAM_DataBase:
    con = None

    #Carica il DB nella RAM per maggiori prestazioni
    def __init__(self, path):
        con = sqlite3.connect(path)
    
        #Crea la tabella nel DB (con un utente amministratore default) se non esiste già
        try:
            con.execute('''CREATE TABLE USERS(
                            ID TEXT PRIMARY KEY NOT NULL,
                            ALIAS TEXT NOT NULL,
                            LEVEL INT NOT NULL CHECK(LEVEL >= 0 AND LEVEL <= 2) DEFAULT 0
                        )''')

            con.execute('''INSERT INTO USERS
                            VALUES("EDC138216", "Edoardo", 2)
                        ''')
            con.commit()

        except:
            pass

        #Scrive il DB in un file temporaneo
        con = sqlite3.connect('users.db')
        tempfile = StringIO()
        for line in con.iterdump():
            tempfile.write('%s\n' % line)
        con.close()
        tempfile.seek(0)

        #Crea DB nella RAM e importa dal file temporaneo
        self.con = sqlite3.connect(":memory:", check_same_thread=False)
        self.con.cursor().executescript(tempfile.read())
        self.con.commit()
        self.con.row_factory = sqlite3.Row

    def select_id(self, user_id):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM USERS WHERE ID=?', (user_id,))

        rows = cur.fetchall()
        
        return rows

def broadcast():
    with open("./regFile.txt", "a+") as f:
        f.seek(0)
        line=f.readline()
        while line != '':
            bot.sendMessage(line, "changed profile pic :)")
            line=f.readline()

def handle(msg):
    global db

    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    pprint(msg)

    username = msg['from']['username']
    user_id = msg['from']['id']
    
    if content_type == 'text':
        text = msg['text'].split()

        if text[0] == '/help':

            response = '/help - Visualizza elenco e descrizione dei comandi disponibili\n'+\
                       '/subscribe <User_ID> - Per iscriversi al bot e ricevere messaggi; richiede '+\
                           '<User_ID> per verificare l\'autorizzazione'+\
                       '/broadcast - Invia un messaggio a tutti gli utenti iscritti'

            bot.sendMessage(chat_id, response)

        elif text[0] == '/broadcast':
            broadcast()

        elif text[0] == '/subscribe':

            if len(text) != 2:
                response = 'Wrong command syntax.\n'+\
                           'Usage: /subscribe <User_ID>'

            else:
                rows = db.select_id(text[1])

                if len(rows) == 0:
                    response = 'Permission denied.'
                
                else:
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
                            response = 'You are already subscribed.'
                        else:
                            print(chat_id,  file=f)
                            response = 'You are now subscribed to Diodysus!'
            
            bot.sendMessage(chat_id, response)
    #bot.sendMessage(chat_id, text)
    


TOKEN = '5311475211:AAH6zgzP7dDxqMmQ-UYhGMT7e-nRPQxXpuE'

global db 
db = RAM_DataBase('users.db')

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)