from telegram.update import Update

from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler

import sqlite3
from io import StringIO
import os.path
import logging
import signal
from sys import exit
from hashlib import pbkdf2_hmac

##############################
#   INITIALIZATION
##############################

# Enable logging
logging.basicConfig(
    filename="maintainer_companion_bot.log",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO # DEBUG gives too much sensitive information
)
logger = logging.getLogger("maintainer_companion_bot")

# Handle Ctrl-C
def interrupt_handler(sig, frame):
    logger.info("Shutting Down...\n")
    exit(0)

signal.signal(signal.SIGINT, interrupt_handler)

# Enum user types
ADMIN, MAINTAINER, OBSERVER = range(1, 3+1)

# Enum states for login conversation handler
USERNAME, PASSWORD = range(2)

# Enum states for broadcast conversation handler
FORWARD_MESSAGE = range(1)

SALT = b'?\x9a\xcbnx\x14\x1b \xb7\x19\x1d\x90\xf8\xcd\x93&'
ITERATIONS = 1000

# Class for creation and interaction with RAM DataBase
class RAM_DataBase:
    con = None
    path = str

    # Loads DataBase into RAM for better performance
    def __init__(self, path):
        self.path = path

        try:
            if not os.path.exists(path):
                raise FileNotFoundError("'{}' not found".format(path))
                
            con = sqlite3.connect(path)
        
            # Writes DB in temporary file
            tempfile = StringIO()
            for line in con.iterdump():
                tempfile.write('%s\n' % line)
            con.close()
            tempfile.seek(0)

            # Creates DB in RAM from temporary file
            self.con = sqlite3.connect(":memory:", check_same_thread=False)
            self.con.cursor().executescript(tempfile.read())
            self.con.commit()
            self.con.row_factory = sqlite3.Row

        except Exception as e:
            logger.critical("Unable to load '{}' in RAM. Exception raised: {}".format(self.path, e))
            logger.info("Shutting Down...\n")
            exit(-1)

        logger.info("Successfully loaded '{}' in RAM".format(self.path))

    ### Telegram Users Functions
    # Returns True if username and password hash correspond to existing user
    def check_user(self, username, password_hash):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM USERS WHERE USERNAME=? AND PASSWORD_HASH=?', (username, password_hash))

        rows = cur.fetchall()

        if len(rows) == 0:
            return False
        
        return True

    # Returns user corresponding to username
    def get_user(self, username):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM USERS WHERE USERNAME=?', (username,))

        rows = cur.fetchall()
        
        return rows[0]

    ### Telegram Chats Functions
    # Returns all chats
    def get_chats(self):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM CHATS')

        rows = cur.fetchall()
        
        return rows

    # Returns True if chat id already exists
    def check_chat(self, chat_id):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM CHATS WHERE CHAT_ID=?', (chat_id,))

        rows = cur.fetchall()

        if len(rows) == 0:
            return False
        
        return True
    
    # Returns chat corresponding to chat_id
    def get_chat(self, chat_id):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM CHATS WHERE CHAT_ID=?', (chat_id,))

        rows = cur.fetchall()
        
        return rows[0]

    # Adds new chat. Should not give problems regarding already existing chats thanks to login function check
    def new_chat(self, chat_id, username):

        try:
            con = sqlite3.connect(self.path)

            con.execute('''INSERT INTO CHATS
                        VALUES(?, ?)''', (chat_id, username))
            con.commit()

        except:
            return -1

        return 0

    # Removes a chat
    def remove_chat(self, chat_id):

        try:
            con = sqlite3.connect(self.path)

            con.execute('''DELETE FROM CHATS WHERE CHAT_ID=?''', (chat_id,))
            con.commit()

        except Exception as e:
            print(e)
            return -1

        return 0

##############################
#   COMMAND'S HANDLERS
##############################

# START - Command executed when a user starts a chat with the bot
def start(update: Update, context: CallbackContext):

    # Sends reply text
    update.message.reply_text(
        "Welcome to the Maintainer Companion Bot!\n"+\
        "Type /login to authenticate or /help to see a list of all available commands."
    )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    message = update.message.text
    log = "'{}' from {} (Username: {} - Last name: {} - First name: {})".format(message, id, username, last_name, first_name)

    logger.info(log)

# HELP - View a list of all available commands, with brief description
def help(update: Update, context: CallbackContext):

    # Sends reply text
    update.message.reply_text(
        "Below is a list of all available commands, divided by level of required authorization.\n"+\
        "Remember that every command is also available for users with a greater level.\n\n"+\

        "GUEST COMMANDS\n\
            /help - View list of available commands\n\
            /login - Authenticate to interact with the bot\n\n"+\

        "OBSERVER COMMANDS\n\
            /logout - Stop receiving notifications from the bot\n\n"+\

        "MAINTAINER COMMADS\n\
            /placeholder\n\n"+\

        "ADMIN COMMANDS\n\
            /broadcast - Sends a message to all logged users\n\n"  
    )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    message = update.message.text
    log = "'{}' from {} (Username: {} - Last name: {} - First name: {})".format(message, id, username, last_name, first_name)

    logger.info(log)

# LOGIN - Entry point for login procedure
def login(update: Update, context: CallbackContext):
    global telegram_db
    can_proceed = True

    # If chat_id already exists, some user is already logged from the device
    if telegram_db.check_chat(update.message.chat.id):
        # Sends reply text
        update.message.reply_text(
            "Already logged from this device, use /logout if you want to exit."   
        )

        can_proceed = False

    else:
        # Sends reply text
        update.message.reply_text(
            "Type your username, or /cancel to end login procedure."   
        )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    message = update.message.text
    log = "'{}' from {} (Username: {} - Last name: {} - First name: {})"\
            .format(message, id, username, last_name, first_name)

    logger.info(log)

    # Advance conversation to returned state
    if can_proceed:
        return USERNAME
        
    else:
        return ConversationHandler.END
       

# LOGOUT - User logout from current device
def logout(update: Update, context: CallbackContext):
    global telegram_db
    exception = None

    try:
        # Updates db file deleting chat, then reloads it in RAM
        if telegram_db.remove_chat(update.message.chat.id) >= 0:
            telegram_db = RAM_DataBase(telegram_db.path)

        else:
            raise Exception("Error while removing chat")

        # Sends reply text
        update.message.reply_text(
            "Logout successful."
        )

    except Exception as e:
        exception = e

    finally:
        # Retrieves useful infos for logging purposes and creates log message
        user = update.message.from_user
        id = user.id
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        message = update.message.text
        log = "'{}' from {} (Username: {} - Last name: {} - First name: {})".format(message, id, username, last_name, first_name)

        if exception != None:
            logger.error(log + " raised exception {}".format(exception))
        else:
            logger.warning(log)

# BROADCAST - Entry point for broadcast messaging (function only available for administrators)
def broadcast(update: Update, context: CallbackContext):
    global telegram_db
    can_proceed = True

    chat_id = update.message.chat.id

    # If chat_id doesn't exist, user is not logged and can't perform operation
    if not telegram_db.check_chat(chat_id):
        # Sends reply text
        update.message.reply_text(
            "You must be logged with /login to perform this operation."   
        )

        can_proceed = False

    else:
        # If logged user is not an administrator, end conversation
        if telegram_db.get_user(telegram_db.get_chat(chat_id)["username"])["level"] != ADMIN:
            # Sends reply text
            update.message.reply_text(
                "Permission denied."   
            )

            can_proceed = False

        else:
            # Sends reply text
            update.message.reply_text(
                "Type your message, or /cancel to end broadcast procedure."   
            )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    message = update.message.text
    log = "'{}' from {} (Username: {} - Last name: {} - First name: {})"\
            .format(message, id, username, last_name, first_name)

    logger.info(log)

    # Advance conversation to returned state
    if can_proceed:
        return FORWARD_MESSAGE
    else:
        return ConversationHandler.END 

# Filters out unknown commands
def unknown(update: Update, context: CallbackContext):

    # Sends reply text
    update.message.reply_text(
        "Unrecognized command '{}'. Type /help for a list of all available commands.".format(update.message.text)
    )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    message = update.message.text
    log = "Unrecognized '{}' from {} (Username: {} - Last name: {} - First name: {})"\
            .format(message, id, username, last_name, first_name)

    logger.info(log)

##############################
#   UTILITIES
##############################

# Ends current conversation
def cancel(update: Update, context: CallbackContext):

    # Sends reply text
    update.message.reply_text(
        "Procedure cancelled."
    )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    log = "Procedure cancelled from {} (Username: {} - Last name: {} - First name: {})"\
            .format(id, username, last_name, first_name)

    logger.info(log)

    # Ends conversation
    return ConversationHandler.END

# Stores username and requires password
def username(update: Update, context: CallbackContext):

    # Saves received text as username in current conversation context
    context.user_data["username"] = update.message.text

    # Sends reply text
    update.message.reply_text(
        "Type your password, or /cancel to end login procedure."  
    )

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    log = "Login procedure: received username from {} (Username: {} - Last name: {} - First name: {})"\
            .format(id, username, last_name, first_name)

    logger.info(log)
    
    # Advance conversation to returned state
    return PASSWORD

# Reads password and checks for authentication 
def password(update: Update, context: CallbackContext):
    global telegram_db
    exception = None
    logged = False

    try:
        chat_id = update.message.chat.id

        # Hashes messange user message containing password and deletes it
        password_hash = pbkdf2_hmac('sha256', update.message.text.encode(), SALT, ITERATIONS).hex()
        update.message.delete() 

        # Read username from current conversation context
        context_username = context.user_data["username"]

        # Authenticates
        logged = telegram_db.check_user(context_username, password_hash)

        if logged: 
            logged_user = telegram_db.get_user(context_username)

            # Updates db file creating new chat, then reloads it in RAM
            if telegram_db.new_chat(chat_id, context_username) >= 0:
                telegram_db = RAM_DataBase(telegram_db.path)

            else:
                raise Exception("Error while creating chat")

            # Sends reply text
            if logged_user["level"] == 1:
                update.message.reply_text(
                    "Login successful as Administrator."
                ) 
            elif logged_user["level"] == 2:
                update.message.reply_text(
                    "Login successful as Maintainer."
                ) 
            elif logged_user["level"] == 3:
                update.message.reply_text(
                    "Login successful as Observer."
                )        
        else:
            update.message.reply_text(
                "Login failed: wrong username or password."  
            )

    except Exception as e:
        exception = e
    
    finally:
        # Retrieves useful infos for logging purposes and creates log message
        user = update.message.from_user
        id = user.id
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        context_username = context.user_data["username"]

        if logged:
            log = "Login procedure: access granted to {} for user '{}' (Username: {} - Last name: {} - First name: {})"\
                    .format(id, context_username, username, last_name, first_name)
        else:
            log = "Login procedure: access denied to {} for user '{}' (Username: {} - Last name: {} - First name: {})"\
                    .format(id, context_username, username, last_name, first_name)

        if exception != None:
            logger.error(log + " raised exception {}".format(exception))
        else:
            if logged:
                logger.info(log)
            else:
                logger.warning(log)

        # End conversation
        return ConversationHandler.END

# Sends broadcast message to all logged users
def forward_message(update: Update, context: CallbackContext):
    global telegram_db

    message = update.message.text
    bot = context.bot

    # Sends text to all logged users
    active_chats = telegram_db.get_chats()

    for chat in active_chats:
        bot.send_message(chat["chat_id"], "MESSAGE FROM ADMINS:\n" + message)

    # Retrieves useful infos for logging purposes and creates log message
    user = update.message.from_user
    id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    log = "Broadcast: message '{}' from {} (Username: {} - Last name: {} - First name: {})"\
            .format(message, id, username, last_name, first_name)

    logger.info(log)
    
    # Advance conversation to returned state
    return ConversationHandler.END

##############################
#   MAIN
##############################

# Run bot
def main():

    # Loads DB in RAM
    global telegram_db

    telegram_db = RAM_DataBase("telegram.db")

    # Initializes bot t.me/maintainer_companion_bot
    logger.info("Starting...")
    updater = Updater("5367789080:AAGVQ-CC1YFSif5pni6c_n4tK0LTJD8TIBE", use_context=True)

    # Initializes conversation handlers
    login_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USERNAME: [MessageHandler(Filters.text & (~Filters.command), username)],
            PASSWORD: [MessageHandler(Filters.text & (~Filters.command), password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler('broadcast', broadcast)],
        states={
            FORWARD_MESSAGE: [MessageHandler(Filters.text & (~Filters.command), forward_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Commands, conversation and messages' handlers
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('logout', logout))

    updater.dispatcher.add_handler(login_handler)
    updater.dispatcher.add_handler(broadcast_handler)

    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Run the bot until the user presses Ctrl-C
    logger.info("Listening...")
    updater.start_polling()


if __name__ == "__main__":
    main()