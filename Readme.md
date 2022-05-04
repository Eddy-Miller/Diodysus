# Diodysus
Un progetto che non mi pento di definire BELLO

Posizionarsi nella cartella del progetto

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
- /help per ottenere la lista dei comandi supportati (con breve descrizione)
- /register <Admin_ID> <New_ID> <New_Alias> [New_Level] - Per registrare al bot un nuovo utente, a cui saranno assegnati <New_ID> univoco, <New_Alias> e [New_Level]; operazione disponibile solo agli amministratori. Il livello (opzionale e di default 0) indica il ruolo: 2 - Amministratore, 1 - Manutentore, 0 - Guest
- /subscribe <User_ID> per iscriversi al bot, richiede <User_ID> per l'autenticazione
- /users <Admin_ID> - Visualizza tutti gli utenti registrati; operazione disponibile solo agli amministratori
- /broadcast <message> - Invia <message> a tutti gli utenti iscritti
- /multicast <User_ID> <level> <message> - Invia <message> a tutti gli utenti iscritti di livello uguale o superiore a <level>, specificando l'utente inviante, che a sua volta deve essere di livello uguale o superiore a <level>

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