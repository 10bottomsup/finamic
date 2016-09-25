import requests
import json
import datetime

class Quandl:
	def __init__( self, q_token, region, access_key, secret_key, table ):
		self.region = region
		self.access_key = access_key
		self.secret_key = secret_key
		self.qtoken = token
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
			self.stock_name = jvtype[1]
			# self.market = 'WIKI'

			self.t = datetime.datetime.now()
			self.curr_time = self.t.strftime( '%y-%m-%d' )

			url =  "https://www.quandl.com/api/v3/datasets/WIKI/" + self.stock_name + ".json?start_date=" + self.date_period + "&end_date=" + self.curr_time + "&collapse=monthly&api_key=" + self.qtoken

			self.response = requests.get( url )
			return self.response['dataset']['data']

		elif jvtype == 2:
			self.table = self._get_dynamodb_table()
			self.response = self.table.query() # do something

	def process_data( self, jvtype, jvdata ):
		self.jv_data = self._download_data( type, jvtype, jvdata )
		self.jv_len = len( self.jv_data )

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

		self.q_change = ( self.q_close_max - self.q_close_min )*100 / self.q_close_max
		self.ctr = 0
		self.k = 0

		for i in l1_list:
			self.qval = self.q_change * i
			self.ctr = k
			self.k = 0
			for j in xrange( self.ctr, len(self.q_close) ):
				if j > self.qval:
					self.level1.append( { i: self.k } )
					break
				else:
					self.k += 1


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