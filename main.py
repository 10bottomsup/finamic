from flask import Flask, request, jsonify
import json
import credentials
import apiai
import requests
import datetime
import boto3
from boto3.dynamodb.conditions import Key, Attr

# from src import *

app = Flask( __name__ )
app.config.from_object( credentials )

def get_dynamodb_table():
	boto3.setup_default_session(
				region_name= app.config[ 'AWS_DEFAULT_REGION' ],
				aws_access_key_id= app.config[ 'AWS_USER_ACCESS_KEY_ID' ],
				aws_secret_access_key= app.config[ 'AWS_USER_SECRET_ACCESS_KEY' ]
			)
	client = boto3.resource( 'dynamodb' )
	return client.Table( app.config[ 'AWS_DYNAMODB_TABLE' ] )

def gen_uuid4():
	return uuid.uuid4()

class APIAIX:
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

class Quandl:
	def __init__( self, q_token, region, access_key, secret_key, table ):
		self.region = region
		self.access_key = access_key
		self.secret_key = secret_key
		self.qtoken = q_token
		self.table = table

	def _get_dynamodb_table( self ):
		boto3.setup_default_session(
					region_name= self.region,
					aws_access_key_id= self.access_key,
					aws_secret_access_key= self.secret_key
				)
		client = boto3.resource( 'dynamodb' )
		return client.Table( app.config[ 'AWS_DYNAMODB_TABLE' ] )

	def _download_data( self, jvtype, jvdata ):
		if jvtype == 1:
			self.date_period = jvdata[0]
			self.stock_name = jvdata[1]
			# self.market = 'WIKI'

			self.t = datetime.datetime.now()
			self.curr_time = self.t.strftime( '%Y-%m-%d' )

			url =  "https://www.quandl.com/api/v3/datasets/WIKI/" + self.stock_name + ".json?start_date=" + self.date_period + "&end_date=" + self.curr_time + "&collapse=monthly&order=asc&api_key=" + self.qtoken

			self.response = requests.get( url )
			self.res = json.loads( self.response.text )
			return self.res['dataset']['data']

		elif jvtype == 2:
			self.table = self._get_dynamodb_table()
			self.response = self.table.query() # do something

	def process_data( self, jvtype, jvdata ):
		self.jv_data = self._download_data( jvtype, jvdata )
		self.jv_len = len( self.jv_data )

		self.q_date = list()
		self.q_open = list()	
		self.q_close = list()
		self.q_high = list()
		self.q_low = list()
		self.q_volume = list()
		self.q_exd = list()
		self.q_sr = list()

		for self.dset in self.jv_data:
			self.q_date.append( self.dset[0] )
			self.q_open.append( self.dset[1] )
			self.q_high.append( self.dset[2] )
			self.q_low.append( self.dset[3] )
			self.q_close.append( self.dset[4] )
			self.q_volume.append( self.dset[5] )
			self.q_exd.append( self.dset[6] )
			self.q_sr.append( self.dset[7] )


		#level 1
		self.l1_list = [ 45, 30, 15, 10 ]
		self.level1 = []
		
		self.q_close_min = min( self.q_close )
		self.q_close_max = max( self.q_close )

		self.q_change = ( self.q_close_max - self.q_close_min )
		self.ctr = 0
		self.k = 0

		self.qv = 0
		self.q_up = self.q_close_min
		for i,v in enumerate( self.l1_list ):
			self.q_down = self.q_up
			self.q_up = self.q_close_min + self.q_change * sum( self.l1_list[0:i+1] )/100

			for v1 in self.q_close:
				if self.q_down <= v1 < self.q_up:
					self.k += 1
			self.level1.append( {v: self.k} )
			self.k = 0

		# level 2
		self.level2 = []
		self.level2.append( { 'header': 'test' } )
		self.level2.append( { 'OPEN': sum(self.q_open)/len(self.q_open) } )
		self.level2.append( { 'HIGH': sum(self.q_high)/len(self.q_high) } )
		self.level2.append( { 'LOW': sum(self.q_low)/len(self.q_low) } )
		self.level2.append( { 'CLOSE': sum(self.q_close)/len(self.q_close) } )
		self.level2.append( { 'VOL': sum(self.q_volume)/len(self.q_volume) } )
		self.level2.append( { 'EXD': sum(self.q_exd)/len(self.q_exd) } )
		self.level2.append( { 'SR': sum(self.q_sr)/len(self.q_sr) } )

		# level 3
		self.level3 = []
		for i, d in enumerate( self.q_date ):
			self.m = d.split( '-' )[1]
			self.m1 = datetime.datetime.strptime( self.m, '%m' )
			self.m2 = self.m1.strftime( '%b' )

			self.level3.append( { self.m2: self.q_open[i] } )

		return { 
			'level1': self.level1, 
			'level2': self.level2,
			'level3': self.level3
		}

class Bridge:
	def __init__(self, access_key, region, secret_key ):
		self.region = region
		self.secret_key = secret_key
		self.access_key = access_key

	def _get_dynamodb_table( self ):
		boto3.setup_default_session(
					region_name= self.region,
					aws_access_key_id= self.access_key,
					aws_secret_access_key= self.secret_key
				)
		client = boto3.resource( 'dynamodb' )
		return client.Table( app.config[ 'AWS_DYNAMODB_TABLE_STOCK_NAME' ] )

	def _stock_mapper( self, co_name ):
		self.table = self._get_dynamodb_table()
		self.response = self.table.scan( FilterExpression=Attr('co_name').contains( co_name ))
		self.stock_name = self.response['Items'][0]['stock_name']
		return self.stock_name

	def configure_type( self, params ):
		t = datetime.datetime.now()
		curr_time = t.strftime( '%Y-%m-%d' )

		self.date_period = None
		self.btype = 1

		if 'syn' in params:
			self.btype = 2
			if 'date-period' in params:
				self.date_period = params[ 'date-period' ]
			return self.btype, self.date_period

		else:
			self.btype = 1
			self.date_period = params['parameters']['date-period'].split('/')[0]
			self.co_name = params['parameters'][ 'given-name' ]
			self.stock_name = self._stock_mapper( self.co_name )
			return self.btype, [ self.date_period, self.stock_name ]

@app.route( '/v1/mobile_app', methods=[ 'POST' ] )
def mobile_app():
	if request.method == 'POST':
		text = request.json[ 'text' ] or None

		if text == None:
			return 'Invalid text', 400

		xapiai = APIAIX( app.config[ 'APIAI_ACCESS_TOKEN' ] )
		apiai_params = xapiai.parse_intent( text )

		jv_bdg = Bridge(
			app.config[ 'AWS_USER_ACCESS_KEY_ID' ],
			app.config[ 'AWS_DEFAULT_REGION' ],
			app.config[ 'AWS_USER_SECRET_ACCESS_KEY' ]
		)
		req_type, jv_params = jv_bdg.configure_type( apiai_params )

		quandl = Quandl(
			app.config['QUANDL_API_KEY'],
			app.config[ 'AWS_DEFAULT_REGION' ],
			app.config[ 'AWS_USER_ACCESS_KEY_ID' ],
			app.config[ 'AWS_USER_SECRET_ACCESS_KEY' ],
			app.config[ 'AWS_DYNAMODB_TABLE_PERF_ANNUAL' ]
		)
		quandl_data = quandl.process_data( req_type, jv_params )

		return jsonify( quandl_data ), 201

if __name__ == '__main__':
	app.run( debug=True, port=8080 )