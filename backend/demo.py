import json, os
from decimal import Decimal
from boto3.dynamodb.conditions import Key
import boto3
ORIGIN='https://lijiabao-2526.github.io'
def handler(event,context):
    headers={'Content-Type':'application/json','Access-Control-Allow-Origin':ORIGIN,'Cache-Control':'no-store','Access-Control-Allow-Methods':'GET,OPTIONS','X-Content-Type-Options':'nosniff'}
    if event.get('httpMethod')=='OPTIONS':return {'statusCode':204,'headers':headers,'body':''}
    if event.get('httpMethod')!='GET':return {'statusCode':405,'headers':headers,'body':json.dumps({'error':'Read only'})}
    table=boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])
    # Only a reserved synthetic series is exposed, never caller-selected subjects.
    rows=table.query(KeyConditionExpression=Key('device_id').eq('website-synthetic-demo'),ScanIndexForward=False,Limit=30)['Items']
    rows=[{'timestamp':r['timestamp'],'heart_rate':float(r['heart_rate'])} for r in rows if r.get('synthetic') is True]
    rows.sort(key=lambda r:r['timestamp'])
    return {'statusCode':200,'headers':headers,'body':json.dumps({'source':'AWS DynamoDB','synthetic':True,'device_id':'website-synthetic-demo','readings':rows,'ai_connected':False})}
