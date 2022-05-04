# importing all required libraries
# this telegram client use my telegram accounts
from email import message
import telebot
import sys
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events


class ClientTelegram:
	# get your api_id, api_hash, token
	# from telegram as described above
	api_id = 17967690
	api_hash = '7cefeec7df4bc97ee80bfa9435abc8cb'
	# token = '5311475211:AAH6zgzP7dDxqMmQ-UYhGMT7e-nRPQxXpuE'
	message = str # "Working..."

	# your phone number
	phone = '+393806934997'

	# bot info
	bot_name = '@diodysusbot'
	bot_id = 5311475211
	bot_hash = 0 # '68411B8A2A75FF0884DF94F8A278BAB277F0CE1C'

	# user info Ion
	user_id = 425612909
	user_hash = 0


	# function to create telegram client
	def connectClient(self, phone, api_id, api_hash):
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

		return client

	def sendMessage(self, message, client, bot_name):
		try:
			# receiver user_id and access_hash, use
			# my user_id and access_hash for reference
			#receiver = InputPeerUser(user_id, user_hash)

			# sending message using telegram client to user
			#client.send_message(receiver, message, parse_mode='html')


			# send a message to bot @diodysusbot
			# get entity form bot_name 
			entity = client.get_entity(bot_name)
			client.send_message(entity=entity, message=message, parse_mode='html')

		except Exception as e:
			
			# there may be many error coming in while like peer
			# error, wrong access_hash, flood_error, etc
			print(e)

	def disconnectClient(self, client):
		# disconnecting the telegram session
		client.disconnect()

	def __init__(self, message):
		self.message = message
		client = self.connectClient(phone=self.phone, api_id=self.api_id, api_hash=self.api_hash)
		self.sendMessage(self.message, client, self.bot_name)
		self.disconnectClient(client=client)


if __name__ == "__main__":
	# recupero il messaggio da inviare da linea di comando
	# message = sys.argv[1]

	# messaggio già inserito per i test
	message = 'ciaooo'

	clientTelegram = ClientTelegram(message=message)






