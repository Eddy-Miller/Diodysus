# Diodysus
Un progetto che non mi pento di definire BELLO
## Telegram Bot @diodysusbot
Inizializzazione dell'ambiente virtuale
```
python -m venv bot_env
source bot_env/bin/activate
```
Installazione di Telepot (python interface to Telegram Bot API)
```
pip install telepot
pip install pprint
```
per far partire il bot eseguire il file botysus.py nella cartella diodo bot.
### Comandi implementati
- /help per ottenere la lista dei comandi supportati (con descrizione)
- /subscribe per iscriversi al bot, richiede un ID di autenticazione
- /broadcast per mandare un messaggio a tutti gli utenti sottoscritti al bot