# importing all required libraries
# this telegram client use my telegram accounts
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events


# get your api_id, api_hash, token
# from telegram as described above
api_id = 17967690
api_hash = '7cefeec7df4bc97ee80bfa9435abc8cb'
# token = '5311475211:AAH6zgzP7dDxqMmQ-UYhGMT7e-nRPQxXpuE'
message = "Working..."



# your phone number
phone = '+393806934997'

# bot info
bot_name = '@diodysusbot'
bot_id = 5311475211
bot_hash = 0 # '68411B8A2A75FF0884DF94F8A278BAB277F0CE1C'

# user info Ion
user_id = 425612909
user_hash = 0

# creating a telegram session and assigning
# it to a variable client
client = TelegramClient('session', api_id, api_hash)

# connecting and building the session
client.connect()

# in case of script ran first time it will
# ask either to input token or otp sent to
# number or sent or your telegram id
if not client.is_user_authorized():

	client.send_code_request(phone)
	
	# signing in the client
	client.sign_in(phone, int(input('Enter the code: ')))


try:
	# receiver user_id and access_hash, use
	# my user_id and access_hash for reference
    #receiver = InputPeerUser(user_id, user_hash)

	# sending message using telegram client to user
    #client.send_message(receiver, message, parse_mode='html')


	# send a message to bot @diodysusbot
	# get entity form bot_name 
	entity = client.get_entity(bot_name)
	client.send_message(entity=entity, message='/broadcast', parse_mode='html')

except Exception as e:
	
	# there may be many error coming in while like peer
	# error, wrong access_hash, flood_error, etc
	print(e)

# disconnecting the telegram session
client.disconnect()
