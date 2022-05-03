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
- /help per ottenere la lista dei comandi supportati (con descrizione)
- /subscribe per iscriversi al bot, richiede un ID di autenticazione
- /broadcast per mandare un messaggio a tutti gli utenti sottoscritti al bot

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
