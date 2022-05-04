import telepot
from telepot.loop import MessageLoop
from pprint import pprint
import sqlite3
from io import StringIO
import time

class RAM_DataBase:
    con = None
    path = str

    #Carica il DB nella RAM per maggiori prestazioni
    def __init__(self, path):
        self.path = path
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

    #Ritorna tutti gli utenti
    def select_all(self):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM USERS ORDER BY LEVEL DESC')

        rows = cur.fetchall()
        
        return rows

    #Seleziona l'utente corrispondente all'ID passato
    def select_id(self, user_id):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM USERS WHERE ID=?', (user_id,))

        rows = cur.fetchall()
        
        return rows

    #Inserire un nuovo utente nel DB. Azione effettuabile solo da amministratori
    def register(self, user_id, user_alias, user_level=0):

        con = sqlite3.connect(self.path)
    
        #Aggiunge il nuovo utente
        try:
            con.execute('''INSERT INTO USERS
                           VALUES(?, ?, ?)
                        ''', (user_id, user_alias, user_level))
            con.commit()
            outcome = 'success'
        except Exception as e:
            outcome = e.args[0]

        return outcome

def broadcast(message):
    with open("./regFile.txt", "r") as f:
        f.seek(0)
        line = f.readline()
        while line != '':
            bot.sendMessage(line, message)
            line = f.readline()
            
def multicast(level, message):
    with open("./regFile.txt", "r") as f:
        f.seek(0)
        line = f.readline()
        while line != '':
            temp = line.split()
            print(message)
            if temp[1] >= level:
                bot.sendMessage(temp[0], message)
            line = f.readline()

def handle(msg):
    global db

    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    pprint(msg)

    username = msg['from']['username']
    user_id = msg['from']['id']
    
    if content_type == 'text':
        text = msg['text'].split()

        ### HELP ###
        if text[0] == '/help':

            response = '/help - Visualizza elenco e descrizione dei comandi disponibili\n'+\
                       '/register <Admin_ID> <New_ID> <New_Alias> [New_Level] - Per registrare al bot un nuovo utente, '+\
                           'che poi potrà iscriversi con <New_ID> assegnato; operazione disponibile solo agli amministratori\n'+\
                       '/subscribe <User_ID> - Per iscriversi al bot e ricevere messaggi; richiede '+\
                           '<User_ID> per verificare l\'autorizzazione\n'+\
                       '/users <Admin_ID> - Visualizza tutti gli utenti registrati; operazione disponibile solo agli amministratori\n'+\
                       '/broadcast <Message> - Invia <Message> a tutti gli utenti iscritti\n'+\
                       '/multicast <User_ID> <Level> <Message> - Invia <Message> a tutti gli utenti iscritti di livello uguale '+\
                           'o superiore a <Level>, specificando l\'utente inviante, che a sua volta deve essere di livello uguale '+\
                           'o superiore a <Level>\n'

            bot.sendMessage(chat_id, response)

        ### REGISTER ###
        elif text[0] == '/register':

            if len(text) != 4 and len(text) != 5:
                response = 'Wrong command syntax.\n'+\
                           'Usage: /register <Admin_ID> <New_ID> <New_Alias> [New_Level]'

            else: 
                rows = db.select_id(text[1])

                if len(rows) == 0 or rows[0]['level'] != 2:
                    response = 'Permission denied.'

                else:
                    if len(text) == 4:
                        text.append(0)

                    outcome = db.register(text[2], text[3], text[4])

                    if outcome == 'success':
                        response = 'Level {} user \'{}\' successfully created!'.format(text[4], text[3])
                        db = RAM_DataBase(db.path) #Aggiorna il DB in RAM

                    else:
                        response = outcome

            bot.sendMessage(chat_id, response)
            
        ### SUBSCRIBE ###
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
                        line = f.readline()
                        isRegistered = False
                        while line != '':
                            f_chat_id = line.split()[0]
                            if f_chat_id == (str(chat_id)+"\n"): 
                                isRegistered = True
                            line = f.readline()

                        if isRegistered == True:
                            response = 'You are already subscribed.'
                        else:
                            print(chat_id, rows[0]['level'],  file=f)
                            response = 'You are now subscribed to Diodysus!'
            
            bot.sendMessage(chat_id, response)
    #bot.sendMessage(chat_id, text)

        ### USERS ###
        elif text[0] == '/users':

            if len(text) != 2:
                response = 'Wrong command syntax.\n'+\
                           'Usage: /users <Admin_ID>'

            else:
                rows = db.select_id(text[1])

                if len(rows) == 0 or rows[0]['level'] != 2:
                    response = 'Permission denied.'
                
                else:
                    rows = db.select_all()
                    response = ''
                    for row in rows:
                        #Formatta: ID, "alias" (level)
                        response += row['ID'] + ', \"' + row['ALIAS'] + '\" (' + str(row['LEVEL']) + ')\n'
            
            bot.sendMessage(chat_id, response)

        ### BROADCAST ###
        elif text[0] == '/broadcast':

            if len(text) < 2:
                response = 'Wrong command syntax.\n'+\
                           'Usage: /broadcast <message>'
                bot.sendMessage(chat_id, response)

            else:
                message = ' '.join(text[1:])
                broadcast(message)
        
        ### MULTICAST ###
        elif text[0] == '/multicast':

            if len(text) < 4:
                response = 'Wrong command syntax.\n'+\
                           'Usage: /multicast <User_ID> <level {0,1,2}> <message>'
                bot.sendMessage(chat_id, response)
            
            else:
                rows = db.select_id(text[1])

                if len(rows) == 0 or rows[0]['level'] < int(text[2]):
                        response = 'Permission denied.'
                        bot.sendMessage(chat_id, response)

                else:
                    message = 'Messaggio inviato da {} ('.format(rows[0]['alias'])
                    
                    if rows[0]['level'] == 2:
                        message += 'amministratore)\n'
                    elif rows[0]['level'] == 1:
                        message += 'manutentore)\n'
                    else:
                        message += 'guest)\n'

                    message += ' '.join(text[3:])
                    multicast(text[2], message)


TOKEN = '5311475211:AAH6zgzP7dDxqMmQ-UYhGMT7e-nRPQxXpuE'

global db 
db = RAM_DataBase('users.db')

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)