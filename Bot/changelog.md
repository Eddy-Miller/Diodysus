# Maintainer Companion Bot

## **1.0.0 (Receiver)**
### *[2022-06-23]*
Bot now supports interaction with ThingsBoard, sending to all logged users Level 1 (Major) Alerts when received and Level 2 (Minor) Alerts when the same device sends 3 of them. Note that Telegram doesn't support remove invocation of Bot's Commands, therefore a basic REST API is made with Flask to receive POST request at http://host:5000/alerts, where the payload is the text of the alert message to be forwarded. 

## **0.5.0 (Standalone)**
### *[2022-05-15]*
First functioning version of the Bot (available [here](t.me/maintainer_companion_bot)). Independent from external sources, has a limited number of supported commands.

Uses an internal SQLite3 database with two tables:

* USERS, with columns for username, password (hash), first name, last name and level (1: administrator, 2: maintainer, 3: observer). This part of database is momentarily immutable.
* CHATS, with columns for chat id and username, external key to USERS table.

USERS table is used for authentication during login procedure and logged user's chats ids are saved in CHATS table.  

```
        ----------------------------------------------------
        |                       USERS                      |
        |--------------------------------------------------|
    --->|+USERNAME (TEXT, PK)                              |
    |   |+PASSWORD_HASH (TEXT, NOT NULL)                   |
    |   |+FIRST_NAME (TEXT, NOT NULL)                      |
    |   |+LAST_NAME (TEXT, NOT NULL)                       |
    |   |+LEVEL (INT, NOT NULL, 1 <= LEVEL <= 3, DEFAULT 3)|
    |   ----------------------------------------------------
    |   --------------------------------
    |   |            CHATS             |
    |   |------------------------------|
    |   |+CHAT_ID (INT, PK)            |
    ----|+USERNAME (TEXT, NOT NULL, FK)|
        --------------------------------
    
```

### **Supported Commands**
Below is a list of all available commands, sorted by level required to use them. Every command is always available also for users of higher levels.

**Guest Level**
```
/help - View list of all availabe commands, with bried description

/login - Authentication procedure to enable interactions corresponding to user level
```

**Observer Level**
```
/logout - Exit procedure, user returns to guest level 
```

**Maintainer Level**
```
No commands currently implemented
```

**Admin Level**
```
/broadcast - Sends a message to all logged users
```