import apiai
import os
import sys
import json

class APIAIX( object ):
	def __init__( self, token ):
		self.__token = token
		self.__params = {}

	def parse_intent( self, text ):
		self.ai = apiai.ApiAI( '80aca41b34ee4f8a85da9a26dd690861' )
		self.request = self.ai.text_request()
		self.request.lang = 'en'
		self.request.query = text

		self.response = self.request.getresponse()
		self.resp_text = json.loads( self.response.read() )

		# self.__params['action'] = self.resp_text['result']['action']
		# self.__params['action_incomplete'] = self.resp_text['result']['actionIncomplete']
		# also include the response params
		self.__params['parameters'] = self.resp_text['result']['parameters']

		return self.__params