from datetime import datetime
import datetime

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
		return client.Table( app.config[ 'AWS_DYNAMODB_TABLE' ] )

	def _stock_mapper( self, co_name ):
		self.table = self._get_dynamo_table()
		self.response = self.table.scan( FilterExpression=Attr('co_name').contains( co_name ))
		self.stock_name = self.response['Items']['stock_name']

	def configure_type( params ):
		t = datetime.now()
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
			self.date_period = params[ 'date-period' ]
			self.co_name = params[ 'given-name' ]
			self.stock_name = self._stock_mapper( self.co_name )
			return self.btype, [ self.date_period, self.stock_name ]