import boto3
import uuid
from flask import Flask
import credentials

app = Flask( __name__ )
app.config.from_object( credentials )

def main():
	boto3.setup_default_session(
		region_name= app.config[ 'AWS_DEFAULT_REGION' ],
		aws_access_key_id= app.config[ 'AWS_USER_ACCESS_KEY_ID' ],
		aws_secret_access_key= app.config[ 'AWS_USER_SECRET_ACCESS_KEY' ]
	)

	client = boto3.resource( 'dynamodb' )
	table = client.Table( 'stock_company' )

	i = 1
	with open( 'wiki_cos.csv', 'r') as f:
		for line in f:
			tokens = line.split( ',' )
			co_name = tokens[1].replace( '"', '' )
			market, stock_name = tokens[0].split( '/' )
			uid = str( uuid.uuid4() )

			response = table.put_item(
				Item={
					'_id': uid,
					'market': market,
					'stock_name': stock_name,
					'co_name': co_name.lower(),
				}
			)
			print str(i) + ': ' + str( response['ResponseMetadata']['HTTPStatusCode'] )
			i += 1

		f.close()

	print 'Done'

if __name__ == '__main__':
	main()