# Diodysus
NOTA: README da aggiornare in base alle nuove scelte effettuate

Un progetto che non mi pento di definire BELLO

Posizionarsi nella cartella del progetto

SERIALE FUNZIONALITA' TESTATE: 100%

//TODO: testing eth e infra 

## Telegram Bot @diodysusbot
Inizializzazione dell'ambiente virtuale per il bot telegram
```
cd my_bot
python -m venv bot_env
source bot_env/bin/activate
```
Installazione di Telepot (python interface to Telegram Bot API)
```
pip3 install telepot
pip3 install pprint
```
per far partire il bot eseguire il file botysus.py nella cartella diodo_bot.
```
cd my_bot/diodo_bot
python botysus.py
```
### Comandi implementati
- /help per ottenere la lista dei comandi supportati (con descrizione)
- /register <Admin_ID> <New_ID> <New_Alias> [New_Level] - Per registrare al bot un nuovo utente, a cui saranno assegnati <New_ID> univoco, <New_Alias> e [New_Level]; operazione disponibile solo agli amministratori. Il livello (opzionale e di default 0) indica il ruolo: 2 - Amministratore, 1 - Manutentore, 0 - Guest
- /subscribe <User_ID> per iscriversi al bot, richiede <User_ID> per l'autenticazione
- /users <Admin_ID> - Visualizza tutti gli utenti registrati; operazione disponibile solo agli amministratori
- /broadcast <Message\> - Invia <Message\> a tutti gli utenti iscritti
- /multicast <User_ID> <Level\> <Message\> - Invia <Message\> a tutti gli utenti iscritti di livello uguale o superiore a <Level\>, specificando l'utente inviante, che a sua volta deve essere di livello uguale o superiore a <Level\>

## Telegram Client 
Inizializzazione dell'ambiente virtuale per il client telegram
Successivamente si dovrà vedere come avviare il client
```
cd telegram_client
python -m venv v_env
source v_env/bin/activate
```
Installazione delle dipendenze necessarie 
```
pip3 install telebot
pip3 install telethon
```
##Thingsboard
TODO: rest api payload capire come fare e come gestire la numerosita 


## Info raspberry

Pi_a
- nome_host: raspberrypiA
- nome utente: pi_a
- password: AdminPi_a
- eth0: 192.168.10.11


-nome utente Postgres : postgres
-password Postgres : AdminPi_a

Pi_b
- nome_host: raspberrypiB
- nome utente: pi_b
- password: AdminPi_b
- eth0: 192.168.10.12

-nome utente Postgres : postgres
-password Postgres : AdminPi_b


CONNESSIONE DA REMOTO:

IP pubblico: 79.10.213.121  
SSH porta Pi_a: 2221  
SSH porta Pi_b: 2222   
Thingboard porta Pi_a: 8081  
Thingboard porta Pi_a: 8082  


ip_a interno: 192.168.1.15   
ip_b interno: 192.168.1.16  

ES: comando per collegarsi <ssh pi_a@79.10.213.121 -p 2221>

